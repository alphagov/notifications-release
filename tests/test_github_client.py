import base64

import pytest

from app import github_client


@pytest.fixture(autouse=True)
def clear_client_caches():
    for function in (
        github_client.list_commits,
        github_client.list_pull_requests,
        github_client.compare_commits,
        github_client.get_contents,
    ):
        function.cache.clear()


def test_get_sends_authenticated_request_and_returns_json(monkeypatch):
    response_payload = {"login": "developer"}
    response = type(
        "Response",
        (),
        {"ok": True, "json": lambda self: response_payload},
    )()
    request = {}

    def fake_get(url, **kwargs):
        request["url"] = url
        request.update(kwargs)
        return response

    monkeypatch.setattr(github_client.requests, "get", fake_get)

    result = github_client._get("github-token", "/user")

    assert result == response_payload
    assert request == {
        "url": "https://api.github.com/user",
        "headers": {
            "Authorization": "Bearer github-token",
            "Accept": "application/vnd.github+json",
        },
        "params": None,
        "timeout": 10,
    }


@pytest.mark.parametrize(
    ("function", "args", "expected_path", "expected_params"),
    [
        (github_client.get_authenticated_user, ("token",), "/user", None),
        (
            github_client.get_repo,
            ("token", "octo", "widgets"),
            "/repos/octo/widgets",
            None,
        ),
        (
            github_client.list_commits,
            ("token", "octo", "widgets"),
            "/repos/octo/widgets/commits",
            {"per_page": 30},
        ),
        (
            github_client.list_pull_requests,
            ("token", "octo", "widgets"),
            "/repos/octo/widgets/pulls",
            {"state": "all", "per_page": 30, "sort": "updated", "direction": "desc"},
        ),
        (
            github_client.compare_commits,
            ("token", "octo", "widgets", "base", "head"),
            "/repos/octo/widgets/compare/base...head",
            None,
        ),
        (
            github_client.get_contents,
            ("token", "octo", "widgets", "README.md"),
            "/repos/octo/widgets/contents/README.md",
            None,
        ),
    ],
)
def test_api_helpers_request_expected_endpoint(
    monkeypatch, function, args, expected_path, expected_params
):
    request = {}

    def fake_get(token, path, params=None):
        request.update(token=token, path=path, params=params)
        return {"result": "ok"}

    monkeypatch.setattr(github_client, "_get", fake_get)

    assert function(*args) == {"result": "ok"}
    assert request == {
        "token": args[0],
        "path": expected_path,
        "params": expected_params,
    }


def test_get_raises_github_api_error_with_response_details(monkeypatch):
    response = type(
        "Response",
        (),
        {
            "ok": False,
            "status_code": 404,
            "json": lambda self: {"message": "Not Found"},
        },
    )()
    monkeypatch.setattr(github_client.requests, "get", lambda *args, **kwargs: response)

    with pytest.raises(github_client.GitHubApiError, match="Not Found") as error:
        github_client._get("token", "/missing")

    assert error.value.status_code == 404


def test_get_contents_decodes_base64_file_content(monkeypatch):
    encoded_content = base64.b64encode(b"hello, world").decode("ascii")
    item = {"encoding": "base64", "content": encoded_content}
    monkeypatch.setattr(github_client, "_get", lambda *args: item)

    result = github_client.get_contents("token", "octo", "widgets", "README.md")

    assert result == {
        "encoding": "base64",
        "content": encoded_content,
        "decoded_content": "hello, world",
    }


def test_get_contents_leaves_directory_listing_unchanged(monkeypatch):
    directory = [{"name": "README.md", "type": "file"}]
    monkeypatch.setattr(github_client, "_get", lambda *args: directory)

    assert github_client.get_contents("token", "octo", "widgets") is directory
