from app import config, pull_request_board
from app.github_client import GitHubApiError


def make_pull_request(number, state, merged_at=None, merge_commit_sha=None):
    return {
        "html_url": f"https://github.com/alphagov/notifications-api/pull/{number}",
        "number": number,
        "title": f"Pull request {number}",
        "state": state,
        "merged_at": merged_at,
        "merge_commit_sha": merge_commit_sha,
        "updated_at": "2026-10-11T00:00:00Z",
        "user": {"login": "developer", "avatar_url": "https://example.com/avatar.png"},
        "head": {"ref": f"branch-{number}"},
    }


def make_environment(environment_id, api_sha=None, admin_sha=None):
    return {
        "id": environment_id,
        "api": {"git_commit": api_sha},
        "admin": {"git_commit": admin_sha},
    }


def test_environment_priority_uses_configured_environments_in_deployment_order(monkeypatch):
    monkeypatch.setattr(
        config,
        "ENVIRONMENTS",
        [{"id": "staging"}, {"id": "preview"}, {"id": "production"}],
    )

    assert pull_request_board._environment_priority() == [
        "production",
        "staging",
        "preview",
    ]


def test_deployed_sha_selects_the_repository_component():
    cases = [
        ("notifications-api", make_environment("production", api_sha="api-sha"), "api-sha"),
        (
            "notifications-admin",
            make_environment("production", admin_sha="admin-sha"),
            "admin-sha",
        ),
        ("notifications-other", make_environment("production", api_sha="api-sha"), None),
    ]

    for repo_id, environment, expected_sha in cases:
        assert pull_request_board._deployed_sha(environment, repo_id) == expected_sha


def test_build_board_groups_pull_requests_by_state_and_deployment(monkeypatch):
    open_pr = make_pull_request(1, "open")
    closed_pr = make_pull_request(2, "closed")
    production_pr = make_pull_request(3, "closed", "2026-10-10T00:00:00Z", "production-sha")
    staging_pr = make_pull_request(4, "closed", "2026-10-09T00:00:00Z", "staging-sha")
    unreleased_pr = make_pull_request(5, "closed", "2026-10-08T00:00:00Z", "unreleased-sha")

    monkeypatch.setattr(
        pull_request_board.github_client,
        "list_pull_requests",
        lambda *args: [open_pr, closed_pr, production_pr, staging_pr, unreleased_pr],
    )
    monkeypatch.setattr(
        pull_request_board.github_client,
        "list_commits",
        lambda *args: [{"sha": "head-sha"}],
    )
    comparisons = {
        "production-sha-base": ["staging-sha", "unreleased-sha", "head-sha"],
        "staging-sha-base": ["unreleased-sha", "head-sha"],
    }

    def compare_commits(token, owner, repo, base, head):
        return {"commits": [{"sha": sha} for sha in comparisons[base]]}

    monkeypatch.setattr(
        pull_request_board.github_client,
        "compare_commits",
        compare_commits,
    )

    board = pull_request_board.build_board(
        "token",
        "alphagov",
        "notifications-api",
        "notifications-api",
        [
            make_environment("production", api_sha="production-sha-base"),
            make_environment("staging", api_sha="staging-sha-base"),
        ],
    )

    assert board == {
        "open": [open_pr],
        "merged": [unreleased_pr],
        "staging": [staging_pr],
        "production": [production_pr],
    }


def test_build_board_keeps_merged_prs_in_merged_column_when_commit_lookup_fails(monkeypatch):
    open_pr = make_pull_request(1, "open")
    merged_pr = make_pull_request(2, "closed", "2026-10-10T00:00:00Z", "merge-sha")
    monkeypatch.setattr(
        pull_request_board.github_client,
        "list_pull_requests",
        lambda *args: [open_pr, merged_pr],
    )

    def fail_to_list_commits(*args):
        raise GitHubApiError(500, "GitHub unavailable")

    monkeypatch.setattr(
        pull_request_board.github_client,
        "list_commits",
        fail_to_list_commits,
    )

    board = pull_request_board.build_board(
        "token",
        "alphagov",
        "notifications-api",
        "notifications-api",
        [make_environment("production", api_sha="production-sha")],
    )

    assert board["open"] == [open_pr]
    assert board["merged"] == [merged_pr]
    assert board["staging"] == []
    assert board["production"] == []


def test_build_board_continues_to_staging_when_production_comparison_fails(monkeypatch):
    merged_pr = make_pull_request(1, "closed", "2026-10-10T00:00:00Z", "staging-merge-sha")
    monkeypatch.setattr(
        pull_request_board.github_client,
        "list_pull_requests",
        lambda *args: [merged_pr],
    )
    monkeypatch.setattr(
        pull_request_board.github_client,
        "list_commits",
        lambda *args: [{"sha": "head-sha"}],
    )

    def compare_commits(token, owner, repo, base, head):
        if base == "production-sha":
            raise GitHubApiError(500, "Comparison unavailable")
        return {"commits": [{"sha": "head-sha"}]}

    monkeypatch.setattr(
        pull_request_board.github_client,
        "compare_commits",
        compare_commits,
    )

    board = pull_request_board.build_board(
        "token",
        "alphagov",
        "notifications-api",
        "notifications-api",
        [
            make_environment("production", api_sha="production-sha"),
            make_environment("staging", api_sha="staging-sha"),
        ],
    )

    assert board["staging"] == [merged_pr]
    assert board["production"] == []
    assert board["merged"] == []
