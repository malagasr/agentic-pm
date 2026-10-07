"""`pm` — the Agentic PM command line.

    pm init                  scaffold agentic-pm.yaml + .env
    pm list                  show available agents
    pm run <agent> [opts]    run an agent
    pm demo                  run release-train + sprint-report on fixture data
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import sys

try:
    from dotenv import load_dotenv
except ImportError:  # optional: plain env vars still work
    def load_dotenv(*_a, **_k):
        return False

load_dotenv()


def cmd_init(_args) -> int:
    for src, dst in (("agentic-pm.yaml.example", "agentic-pm.yaml"),
                     (".env.example", ".env")):
        here = os.path.join(os.path.dirname(__file__), "..", "..", src)
        if os.path.exists(dst):
            print(f"exists, skipping: {dst}")
        elif os.path.exists(here):
            shutil.copy(here, dst)
            print(f"wrote {dst}")
        else:
            print(f"template {src} not found next to package; "
                  f"create {dst} by hand")
    print("Next: edit agentic-pm.yaml (your repos), then `pm demo`.")
    return 0


def cmd_list(_args) -> int:
    import agentic_pm
    for name in sorted(agentic_pm.REGISTRY):
        print(f"{name:18} {agentic_pm.REGISTRY[name].description}")
    return 0


def _emit(text: str, out: str | None, fmt: str) -> int:
    if fmt == "slack":
        print("(slack blocks are returned by render.to_slack; "
              "markdown shown)")
    if out:
        with open(out, "w") as f:
            f.write(text if text.endswith("\n") else text + "\n")
        print(f"wrote {out}")
    else:
        print(text)
    return 0


def cmd_run(args) -> int:
    import agentic_pm
    from . import config as config_mod
    cfg = config_mod.load()
    agent = agentic_pm.get(args.agent)(cfg)
    kwargs = dict(args.extra)
    if args.repo:
        kwargs["repo"] = args.repo
    elif cfg.get("repos"):
        kwargs["repo"] = cfg["repos"][0]
    return _emit(agent.run(**kwargs), args.out, args.format)


def _parse_extra(pairs: list[str]) -> dict:
    kwargs: dict = {}
    for p in pairs:
        if "=" not in p:
            raise SystemExit(f"bad --set value {p!r}; use key=value")
        k, v = p.split("=", 1)
        kwargs[k] = int(v) if v.isdigit() else v
    return kwargs


def cmd_demo(_args) -> int:
    """Run two agents against bundled fixture data — no tokens needed."""
    import agentic_pm
    from .agents import release_train as rt_mod
    from .agents import sprint_report as sr_mod

    fixture_path = os.path.join(os.path.dirname(__file__), "..", "..",
                                "examples", "demo_fixtures.json")
    with open(fixture_path) as f:
        fx = json.load(f)

    # monkeypatch the connector for the demo
    from .connectors import github as gh
    gh.open_pull_requests = lambda repo, client=None: fx["open_prs"]
    gh.open_bugs = lambda repo, client=None: fx["open_bugs"]
    gh.failing_check_runs = lambda repo, client=None: fx["failing_checks"]
    gh.merged_pull_requests = lambda repo, since, client=None: fx["merged_prs"]
    gh.closed_issues = lambda repo, since, client=None: fx["closed_issues"]

    print(agentic_pm.get("release-train")({}).run(repo="demo/repo"))
    print("=" * 60)
    print(agentic_pm.get("sprint-report")({}).run(repo="demo/repo", days=7))
    # silence unused imports (agents register on import)
    _ = (rt_mod, sr_mod)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="pm",
                                     description="AI agents for PM work")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("init", help="scaffold agentic-pm.yaml + .env")
    sub.add_parser("list", help="show available agents")

    run_p = sub.add_parser("run", help="run an agent")
    run_p.add_argument("agent", help="agent name (see `pm list`)")
    run_p.add_argument("--repo", default=None,
                       help="owner/name (defaults to first repo in config)")
    run_p.add_argument("--set", action="append", default=[],
                       help="extra agent kwargs as key=value")
    run_p.add_argument("--out", default=None, help="write to file")
    run_p.add_argument("--format", default="markdown",
                       choices=["markdown", "slack"])

    sub.add_parser("demo", help="run on fixture data, no tokens needed")

    args = parser.parse_args(argv)
    if args.cmd == "init":
        return cmd_init(args)
    if args.cmd == "list":
        return cmd_list(args)
    if args.cmd == "demo":
        return cmd_demo(args)
    if args.cmd == "run":
        args.extra = _parse_extra(args.set)
        return cmd_run(args)
    return 1


if __name__ == "__main__":
    sys.exit(main())
