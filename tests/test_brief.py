"""Tests for the toolkit core + agents (no network, no API keys)."""
import sys
import types

sys.path.insert(0, "src")
# stub httpx: logic tests never touch the network
sys.modules.setdefault("httpx", types.ModuleType("httpx"))

import agentic_pm  # noqa: E402 — registers agents
from agentic_pm.agents.release_train import ReleaseTrainAgent  # noqa: E402
from agentic_pm.render import to_markdown, to_slack  # noqa: E402


def test_registry_lists_three_agents():
    assert {"release-train", "sprint-report",
            "meeting-actions"} <= set(agentic_pm.REGISTRY)


def test_get_unknown_agent_raises_helpfully():
    try:
        agentic_pm.get("nope")
    except ValueError as e:
        assert "release-train" in str(e)
    else:  # pragma: no cover
        raise AssertionError("expected ValueError")


def test_verdict_ladder():
    rt = ReleaseTrainAgent({})
    assert rt._verdict([]).startswith("GO")
    assert rt._verdict(["1 PR(s) open > 14 days"]).startswith("CAUTION")
    assert rt._verdict(["2 critical bug(s) open"]).startswith("NOT READY")
    assert rt._verdict(["failing checks on x"]).startswith("NOT READY")


def test_risk_flags_spot_stale_big_and_critical():
    rt = ReleaseTrainAgent({})
    prs = [{"number": 1, "title": "old", "author": "a",
            "created_at": "2020-01-01", "draft": False, "labels": [],
            "additions": 10, "deletions": 5},
           {"number": 2, "title": "huge", "author": "b",
            "created_at": "2026-10-06", "draft": False, "labels": [],
            "additions": 900, "deletions": 500}]
    bugs = [{"number": 3, "title": "boom", "author": "c",
             "created_at": "2026-10-06", "labels": ["critical"]}]
    flags = rt._risk_flags(prs, bugs, [], stale_days=14, big_lines=1000)
    joined = " ".join(flags)
    assert "14 days" in joined and "oversized" in joined and "critical" in joined


def test_render_markdown_and_slack():
    md = to_markdown("T", [("S", ["a", "b"])])
    assert "# T" in md and "- a" in md
    blocks = to_slack("T", [("S", ["a"])])
    assert blocks[0]["type"] == "header"


def test_meeting_actions_needs_api_key_without_one(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    agent = agentic_pm.get("meeting-actions")({})
    out = agent.run(transcript="hello world")
    assert "ANTHROPIC_API_KEY" in out
