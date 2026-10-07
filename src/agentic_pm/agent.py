"""Base Agent class and registry — the plugin system for the toolkit."""
from __future__ import annotations

REGISTRY: dict[str, type["Agent"]] = {}


class Agent:
    """A PM agent: declare metadata, implement run(), return markdown."""

    name = "base"
    description = "base agent (override me)"

    def __init__(self, config: dict | None = None):
        self.config = config or {}

    def run(self, **kwargs) -> str:
        raise NotImplementedError

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if cls.name != "base":
            REGISTRY[cls.name] = cls


def get(name: str) -> type["Agent"]:
    try:
        return REGISTRY[name]
    except KeyError:
        raise ValueError(
            f"unknown agent '{name}'. Available: {', '.join(sorted(REGISTRY))}"
        ) from None
