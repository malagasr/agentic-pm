"""LLM layer. Works with or without ANTHROPIC_API_KEY.

Without a key, agents fall back to their deterministic output and say so —
the toolkit stays useful on a plane.
"""
from __future__ import annotations

import os

MODEL = "claude-haiku-4-5-20251001"


def available() -> bool:
    return bool(os.environ.get("ANTHROPIC_API_KEY"))


def summarize(prompt: str, max_tokens: int = 200) -> str | None:
    """Return an LLM summary, or None when unavailable."""
    if not available():
        return None
    try:
        import anthropic
        client = anthropic.Anthropic()
        msg = client.messages.create(
            model=MODEL, max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}])
        return msg.content[0].text.strip()
    except Exception:
        return None
