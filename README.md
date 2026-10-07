# Agentic PM

An open toolkit of **AI agents that do product management work** — the chores PMs hate, automated: release readiness, sprint reporting, meeting action items, PR triage, backlog grooming.

The thesis (from [*Why the Agent PM Is Inevitable*](https://aireadypm.com)): the PM's job is coordination overhead, and coordination overhead is exactly what agents eat. This repo is the proof, one agent at a time.

## Try it in 60 seconds (no tokens needed)

```bash
git clone https://github.com/malagasr/agentic-pm.git
cd agentic-pm
pip install -r requirements.txt
PYTHONPATH=src python -m agentic_pm.cli demo
```

`pm demo` runs two agents against bundled fixture data so you can see the output before wiring up anything real.

## Real usage

```bash
cp .env.example .env            # add GITHUB_TOKEN (ANTHROPIC_API_KEY optional)
python -m agentic_pm.cli init   # scaffold agentic-pm.yaml + .env

python -m agentic_pm.cli list
python -m agentic_pm.cli run release-train --repo owner/name
python -m agentic_pm.cli run sprint-report --repo owner/name --set days=14
python -m agentic_pm.cli run meeting-actions --set transcript=notes.txt
python -m agentic_pm.cli run release-train --repo owner/name --out brief.md
```

Without `ANTHROPIC_API_KEY`, agents render deterministic briefs and say so — the toolkit stays useful on a plane. With a key, you get LLM-polished executive summaries.

## The agents

| Agent | Status | What it does |
|---|---|---|
| `release-train` | working | Open PRs + bug queue + CI status → readiness brief (GO / CAUTION / NOT READY) |
| `sprint-report` | working | Merged PRs + closed issues in a window → standup-ready sprint report |
| `meeting-actions` | working | Transcript → action items with owners and due dates (needs API key) |
| `pr-triage` | planned | Rank open PRs by risk, draft review comments |
| `backlog-groomer` | planned | Dedupe, score, and re-rank backlog items |

## Build your own agent

```python
from agentic_pm.agent import Agent

class MyAgent(Agent):
    name = "my-agent"                       # shows up in `pm list`
    description = "what it does"

    def run(self, **kwargs) -> str:         # return markdown
        ...
```

Drop it in `src/agentic_pm/agents/`, import it in `agents/__init__.py`, done — `pm run my-agent` just works. See `sprint_report.py` (~60 lines) for the pattern.

## Architecture

- `agent.py` — base class + registry (the plugin system)
- `config.py` — `agentic-pm.yaml` (repos, thresholds)
- `llm.py` — Anthropic wrapper with graceful no-key fallback
- `render.py` — markdown + Slack Block Kit output
- `connectors/` — data sources (GitHub today; Jira/Linear next)
- `agents/` — one module per agent

## Privacy note

Set your git identity to GitHub's noreply address before your first commit:

```bash
git config user.email "<your-id>+<your-username>@users.noreply.github.com"
```

so your personal email never ends up in public commit history. (Learned the hard way.)

## License

MIT — build on it, ship it, tell us about it.
