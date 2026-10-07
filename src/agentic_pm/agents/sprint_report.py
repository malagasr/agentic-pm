"""Sprint-report agent: merged PRs + closed issues in a window become a
standup-ready sprint report. The chore every PM hates, automated."""
from __future__ import annotations

import datetime

from ..agent import Agent
from ..connectors import github as gh
from ..llm import summarize
from ..render import to_markdown


class SprintReportAgent(Agent):
    name = "sprint-report"
    description = ("Weekly sprint report from merged PRs, closed issues, "
                   "and what's still in flight")

    def run(self, repo: str, days: int = 7, **kwargs) -> str:
        since = (datetime.date.today()
                 - datetime.timedelta(days=days)).isoformat()
        merged = gh.merged_pull_requests(repo, since)
        closed = gh.closed_issues(repo, since)
        in_flight = gh.open_pull_requests(repo)

        sections: list[tuple[str, list[str]]] = [
            ("Shipped", [
                f"#{p['number']} {p['title']} (@{p['author']})"
                for p in merged
            ]),
            ("Closed issues", [
                f"#{i['number']} {i['title']} (@{i['author']})"
                for i in closed
            ]),
            ("Still in flight", [
                f"#{p['number']} {p['title']} (@{p['author']}, "
                f"open since {p['created_at']})"
                for p in in_flight[:10]
            ]),
        ]
        report = to_markdown(
            f"Sprint report — {repo} (last {days}d)", sections)

        if summary := summarize(
                "Write a 4-sentence sprint summary for stakeholders from this "
                f"report. Lead with what shipped:\n\n{report}"):
            report = (f"## TL;DR\n\n{summary}\n\n" + report)
        return report
