"""Meeting-actions agent: transcript in, action items out.

Usage: pm run meeting-actions --transcript notes.txt
Requires ANTHROPIC_API_KEY (extraction quality needs a real model).
"""
from __future__ import annotations

from ..agent import Agent
from ..llm import available, summarize
from ..render import to_markdown


class MeetingActionsAgent(Agent):
    name = "meeting-actions"
    description = "Extract action items (owner, task, due) from a transcript"

    def run(self, transcript: str, **kwargs) -> str:
        if not available():
            return ("meeting-actions needs ANTHROPIC_API_KEY in your .env — "
                    "action-item extraction isn't something to fake "
                    "deterministically.")
        text = transcript
        if len(text) < 6000:
            import os
            if os.path.exists(transcript):
                with open(transcript) as f:
                    text = f.read()
        items = summarize(
            "Extract action items from this meeting transcript. Return a "
            "markdown bullet list, one per line, in the form "
            "'- **[owner or UNASSIGNED]** task (due: date or no date)'. "
            "Be terse; skip discussion with no action.\n\nTranscript:\n"
            + text[:12000],
            max_tokens=600,
        ) or "- extraction failed"
        return to_markdown("Meeting action items",
                           [("Action items", items.splitlines())])
