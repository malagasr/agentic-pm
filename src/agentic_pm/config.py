"""YAML config: team repos, thresholds, agent defaults.

`pm init` writes agentic-pm.yaml from the bundled example.
"""
from __future__ import annotations

import os

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None

DEFAULTS = {
    "github_token_env": "GITHUB_TOKEN",
    "stale_pr_days": 14,
    "big_pr_lines": 1000,
    "repos": [],
}


def load(path: str = "agentic-pm.yaml") -> dict:
    cfg = dict(DEFAULTS)
    if os.path.exists(path):
        if yaml is None:
            raise RuntimeError("pyyaml is required to read config "
                               "(pip install pyyaml)")
        with open(path) as f:
            cfg.update(yaml.safe_load(f) or {})
    return cfg
