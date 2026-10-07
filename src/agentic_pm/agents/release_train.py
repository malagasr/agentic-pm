"""Release-train agent: repo signals in, release-readiness brief out."""
from __future__ import annotations

import datetime

from ..agent import Agent
from ..connectors import github as gh
from ..llm import summarize
from ..render import to_markdown


class ReleaseTrainAgent(Agent):
    name = "release-train"
    description = ("Readiness brief from open PRs, bug queue, and CI status "
                   "(GO / CAUTION / NOT READY)")

    def run(self, repo: str, **kwargs) -> str:
        cfg = self.config
        stale_days = cfg.get("stale_pr_days", 14)
        big_lines = cfg.get("big_pr_lines", 1000)

        prs = gh.open_pull_requests(repo)
        bugs = gh.open_bugs(repo)
        failing = gh.failing_check_runs(repo)
        flags = self._risk_flags(prs, bugs, failing, stale_days, big_lines)

        today = datetime.date.today().isoformat()
        sections: list[tuple[str, list[str]]] = [
            (f"Verdict: {self._verdict(flags)}", []),
            ("Signals", [
                f"Open PRs: **{len(prs)}**",
                f"Open bugs: **{len(bugs)}**",
                f"Failing checks on default branch: **{len(failing)}**",
            ]),
            ("Risk flags", flags),
            ("Oldest open PRs", [
                f"#{p['number']} {p['title']} (@{p['author']}, "
                f"{p['created_at']}, +{p['additions']}/-{p['deletions']})"
                for p in prs[:5]
            ]),
            ("Open bugs", [
                f"#{b['number']} {b['title']} (@{b['author']}, {b['created_at']})"
                for b in bugs[:10]
            ]),
        ]
        brief = to_markdown(f"Release readiness — {repo}", sections)
        brief = (f"_Generated {today} by agentic-pm/release-train_\n\n" + brief)

        if summary := summarize(
                "Write a 3-sentence executive summary of this release-readiness "
                f"brief for a PM:\n\n{brief}"):
            brief = brief.replace("## Signals",
                                  f"## Executive summary\n\n{summary}\n\n## Signals",
                                  1)
        return brief

    @staticmethod
    def _risk_flags(prs, bugs, failing, stale_days, big_lines) -> list[str]:
        def age(d: str) -> int:
            return (datetime.date.today()
                    - datetime.date.fromisoformat(d)).days

        flags: list[str] = []
        stale = [p for p in prs if age(p["created_at"]) > stale_days]
        if stale:
            flags.append(f"{len(stale)} PR(s) open > {stale_days} days "
                         f"(oldest: #{stale[0]['number']})")
        big = [p for p in prs if p["additions"] + p["deletions"] > big_lines]
        if big:
            nums = ", ".join(f"#{p['number']}" for p in big)
            flags.append(f"{len(big)} oversized PR(s) "
                         f"(>{big_lines} lines) — merge risk: {nums}")
        if drafts := [p for p in prs if p["draft"]]:
            flags.append(f"{len(drafts)} draft PR(s) still in flight")
        if failing:
            names = ", ".join(sorted({c["name"] for c in failing}))
            flags.append(f"failing checks on default branch: {names}")
        crit = [b for b in bugs
                if any(x in ("critical", "p0", "sev1") for x in b["labels"])]
        if crit:
            nums = ", ".join(f"#{b['number']}" for b in crit)
            flags.append(f"{len(crit)} critical bug(s) open ({nums})")
        elif bugs:
            flags.append(f"{len(bugs)} open bug(s), none labelled critical")
        return flags

    @staticmethod
    def _verdict(flags: list[str]) -> str:
        if any("critical" in f or "failing checks" in f for f in flags):
            return "NOT READY — resolve red flags first"
        if flags:
            return "CAUTION — shippable with noted risks"
        return "GO — no blockers detected"
