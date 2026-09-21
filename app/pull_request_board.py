"""Groups a repo's pull requests into kanban columns based on where each is deployed.

A merged PR is placed in the furthest-right environment its merge commit has reached,
determined by ancestry against each environment's deployed SHA (reusing the same
deployed-SHA data as the commits view).
"""
from typing import Literal, TypedDict

from app import config, github_client
from app.environment_client import Environment
from app.github_client import GitHubApiError

Column = Literal["open", "merged", "staging", "production"]

# Columns left -> right. Environment ids ("staging", "production") must match config.ENVIRONMENTS.
COLUMNS: list[Column] = ["open", "merged", "staging", "production"]


class PullRequestUser(TypedDict):
    login: str
    avatar_url: str


class PullRequestHead(TypedDict):
    ref: str


class PullRequest(TypedDict):
    html_url: str
    number: int
    title: str
    state: str
    merged_at: str | None
    merge_commit_sha: str | None
    updated_at: str
    user: PullRequestUser
    head: PullRequestHead


Board = dict[Column, list[PullRequest]]


def _environment_priority() -> list[str]:
    """Environment ids ordered furthest-right first, e.g. ["production", "staging"]."""
    ordering = ["production", "staging"]
    env_ids = [env["id"] for env in config.ENVIRONMENTS]
    ordered = [env_id for env_id in ordering if env_id in env_ids]
    ordered += [env_id for env_id in env_ids if env_id not in ordered]
    return ordered


def _deployed_sha(environment: Environment, repo_id: str) -> str | None:
    if repo_id == "api":
        return environment.get("api", {}).get("git_commit")
    if repo_id == "admin":
        return environment.get("admin", {}).get("git_commit")
    return None


def build_board(
    token: str,
    owner: str,
    repo: str,
    repo_id: str,
    environment_statuses: list[Environment],
) -> Board:
    board: Board = {column: [] for column in COLUMNS}

    pull_requests: list[PullRequest] = github_client.list_pull_requests(token, owner, repo)

    head_sha: str | None = None
    try:
        commits = github_client.list_commits(token, owner, repo)
        if commits:
            head_sha = commits[0]["sha"]
    except GitHubApiError:
        head_sha = None

    # For each environment, the set of commit SHAs that are ahead of it (in HEAD but not deployed).
    # A merged commit is deployed to an environment when it is NOT in this set.
    ahead: dict[str, set[str]] = {}
    deployed: dict[str, str] = {}
    for env in environment_statuses:
        env_id = env.get("id")
        deployed_sha = _deployed_sha(env, repo_id)
        if not deployed_sha or not head_sha:
            continue
        deployed[env_id] = deployed_sha
        if deployed_sha == head_sha:
            ahead[env_id] = set()
            continue
        try:
            comparison = github_client.compare_commits(token, owner, repo, deployed_sha, head_sha)
            ahead[env_id] = {commit["sha"] for commit in comparison.get("commits", [])}
        except GitHubApiError:
            # Can't determine ancestry for this env; treat as not deployed there.
            continue

    priority = _environment_priority()

    for pr in pull_requests:
        if pr.get("state") == "open" and not pr.get("merged_at"):
            board["open"].append(pr)
            continue
        if not pr.get("merged_at"):
            # Closed without merging - excluded from the board.
            continue

        merge_sha = pr.get("merge_commit_sha")
        placed: Column = "merged"
        for env_id in priority:
            if env_id in ahead and env_id in deployed and merge_sha not in ahead[env_id]:
                if env_id == "staging" or env_id == "production":
                    placed = env_id
                break
        board[placed].append(pr)

    return board
