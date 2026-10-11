from app import config, github_client
from app.app import app


def authenticate(client):
    with client.session_transaction() as session:
        session["github_token"] = "test-token"
        session["github_user"] = "test-user"


def test_unauthenticated_user_is_redirected_to_login():
    client = app.test_client()

    response = client.get("/")

    assert response.status_code == 302
    assert response.location.endswith("/login")


def test_login_page_is_rendered():
    response = app.test_client().get("/login")

    assert response.status_code == 200
    assert b"You need to sign in with GitHub" in response.data
    assert b"/login/github" in response.data


def test_authenticated_user_can_view_repositories():
    client = app.test_client()
    authenticate(client)

    response = client.get("/repos")

    assert response.status_code == 200
    assert b"API" in response.data
    assert b"/repos/alphagov/notifications-api/commits" in response.data


def test_authenticated_user_can_view_commit_history(monkeypatch):
    client = app.test_client()
    authenticate(client)
    monkeypatch.setattr(
        github_client,
        "list_commits",
        lambda token, owner, repo: [
            {
                "sha": "abc123",
                "html_url": "https://github.com/alphagov/notifications-api/commit/abc123",
                "commit": {
                    "message": "Add a feature",
                    "author": {"name": "Developer", "date": "2026-10-11T12:00:00Z"},
                },
                "author": {"login": "developer", "avatar_url": ""},
            }
        ],
    )
    monkeypatch.setattr(
        "app.app.get_status_for_all_environments",
        lambda: [],
    )

    response = client.get("/repos/alphagov/notifications-api/commits")

    assert response.status_code == 200
    assert b"Add a feature" in response.data
    assert b"abc123" in response.data


def test_disallowed_repository_returns_forbidden():
    client = app.test_client()
    authenticate(client)

    response = client.get("/repos/example/not-allowed/commits")

    assert response.status_code == 403


def test_pull_requests_shortcut_redirects_to_first_configured_repository(monkeypatch):
    client = app.test_client()
    authenticate(client)
    monkeypatch.setattr(
        config,
        "ALLOWED_REPOS",
        [{"id": "repo-id", "name": "Example", "repo": "example/repo"}],
    )

    response = client.get("/pull-requests")

    assert response.status_code == 302
    assert response.location.endswith("/repos/example/repo/pull-requests")


def test_github_error_is_rendered_for_authenticated_request(monkeypatch):
    client = app.test_client()
    authenticate(client)

    def fail_to_get_commits(*args):
        raise github_client.GitHubApiError(500, "GitHub unavailable")

    monkeypatch.setattr(github_client, "list_commits", fail_to_get_commits)
    monkeypatch.setattr(
        "app.app.get_status_for_all_environments",
        lambda: [],
    )

    response = client.get("/repos/alphagov/notifications-api/commits")

    assert response.status_code == 500
    assert b"We couldn&#39;t get data from GitHub" in response.data
    assert b"GitHub unavailable" in response.data


def test_unauthorized_github_error_clears_session_and_redirects_to_login(monkeypatch):
    client = app.test_client()
    authenticate(client)

    monkeypatch.setattr(
        github_client,
        "list_commits",
        lambda *args: (_ for _ in ()).throw(
            github_client.GitHubApiError(401, "Unauthorized")
        ),
    )

    response = client.get("/repos/alphagov/notifications-api/commits")

    assert response.status_code == 302
    assert response.location.endswith("/login")
    with client.session_transaction() as session:
        assert "github_token" not in session
