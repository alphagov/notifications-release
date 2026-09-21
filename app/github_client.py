"""Thin wrapper around the GitHub REST API for the repos this app is allowed to show."""
import base64

import requests

API_BASE_URL = "https://api.github.com"


class GitHubApiError(Exception):
    def __init__(self, status_code, message):
        super().__init__(message)
        self.status_code = status_code


def _get(token, path, params=None):
    response = requests.get(
        f"{API_BASE_URL}{path}",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
        },
        params=params,
        timeout=10,
    )
    if not response.ok:
        raise GitHubApiError(response.status_code, response.json().get("message", "GitHub API error"))
    return response.json()


def get_authenticated_user(token):
    return _get(token, "/user")


def get_repo(token, owner, repo):
    return _get(token, f"/repos/{owner}/{repo}")


def list_commits(token, owner, repo):
    return _get(token, f"/repos/{owner}/{repo}/commits", params={"per_page": 30})


def list_pull_requests(token, owner, repo):
    return _get(
        token,
        f"/repos/{owner}/{repo}/pulls",
        params={"state": "all", "per_page": 30, "sort": "updated", "direction": "desc"},
    )


def compare_commits(token, owner, repo, base, head):
    """Returns the GitHub compare payload; response["commits"] are the commits in head but not in base."""
    return _get(token, f"/repos/{owner}/{repo}/compare/{base}...{head}")


def get_contents(token, owner, repo, path=""):
    """Returns a list (directory) or dict (file) as returned by the GitHub contents API."""
    item = _get(token, f"/repos/{owner}/{repo}/contents/{path}")
    if isinstance(item, dict) and item.get("encoding") == "base64":
        item["decoded_content"] = base64.b64decode(item["content"]).decode("utf-8", errors="replace")
    return item
