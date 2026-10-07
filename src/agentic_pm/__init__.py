"""Agentic PM — AI agents that do product management work."""
from . import agents  # noqa: F401 — registers all agents
from .agent import REGISTRY, get

__all__ = ["REGISTRY", "get"]
__version__ = "0.2.0"
