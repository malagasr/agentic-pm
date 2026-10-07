"""Fetch release-train signals from the GitHub REST API.

Uses only the standard library + httpx. Works unauthenticated for public
repos (rate-limited); set GITHUB_TOKEN for real usage.
"""
from __future__ import annotations

import os
from typing import Any

API = "https://api.github.com"


def _client() -> Any:
    import httpx  # lazy: demo/logic paths never touch the network

    headers = {"Accept": "application/vnd.github+json"}
    if token := os.environ.get("GITHUB_TOKEN"):
        headers["Authorization"] = f"Bearer {token}"
    return httpx.Client(base_url=API, headers=headers, timeout=30)


def open_pull_requests(repo: str, client: Any | None = None) -> list[dict]:
    """Open PRs with review/CI-relevant fields (oldest first)."""
    c = client or _client()
    r = c.get(f"/repos/{repo}/pulls",
              params={"state": "open", "per_page": 100, "sort": "created",
                      "direction": "asc"})
    r.raise_for_status()
    return [
        {"number": pr["number"], "title": pr["title"],
         "author": pr["user"]["login"],
         "created_at": pr["created_at"][:10],
         "draft": pr["draft"],
         "labels": [l["name"] for l in pr["labels"]],
         "additions": pr.get("additions", 0),
         "deletions": pr.get("deletions", 0)}
        for pr in r.json()
    ]


def open_bugs(repo: str, client: Any | None = None) -> list[dict]:
    """Open issues labelled bug (proxy for the bug queue)."""
    c = client or _client()
    r = c.get(f"/repos/{repo}/issues",
              params={"state": "open", "labels": "bug", "per_page": 100,
                      "sort": "created", "direction": "asc"})
    r.raise_for_status()
    return [
        {"number": i["number"], "title": i["title"],
         "author": i["user"]["login"],
         "created_at": i["created_at"][:10],
         "labels": [l["name"] for l in i["labels"]]}
        for i in r.json() if "pull_request" not in i
    ]


def failing_check_runs(repo: str, client: Any | None = None) -> list[dict]:
    """Latest check runs on the default branch that are not green.

    Best-effort: falls back to empty when checks are unavailable.
    """
    c = client or _client()
    try:
        info = c.get(f"/repos/{repo}").json()
        branch = info.get("default_branch", "main")
        ref = c.get(f"/repos/{repo}/commits/{branch}").json()["sha"]
        runs = c.get(f"/repos/{repo}/commits/{ref}/check-runs",
                     params={"per_page": 50}).json().get("check_runs", [])
        return [{"name": r["name"], "status": r["status"],
                 "conclusion": r["conclusion"]}
                for r in runs if r.get("conclusion") not in ("success", "skipped")]
    except Exception:
        return []


def _search(query: str, client: httpx.Client) -> list[dict]:
    r = client.get("/search/issues",
                   params={"q": query, "per_page": 100,
                           "sort": "created", "order": "desc"})
    r.raise_for_status()
    return r.json().get("items", [])


def merged_pull_requests(repo: str, since: str,
                         client: Any | None = None) -> list[dict]:
    """PRs merged on/after `since` (YYYY-MM-DD)."""
    c = client or _client()
    return [
        {"number": pr["number"], "title": pr["title"],
         "author": pr["user"]["login"],
         "created_at": pr["created_at"][:10]}
        for pr in _search(f"repo:{repo} type:pr merged:>={since}", c)
    ]


def closed_issues(repo: str, since: str,
                  client: Any | None = None) -> list[dict]:
    """Issues (not PRs) closed on/after `since` (YYYY-MM-DD)."""
    c = client or _client()
    return [
        {"number": i["number"], "title": i["title"],
         "author": i["user"]["login"],
         "created_at": i["created_at"][:10]}
        for i in _search(f"repo:{repo} type:issue closed:>={since}", c)
    ]
