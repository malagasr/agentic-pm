"""Output renderers: markdown (default) and Slack blocks."""
from __future__ import annotations


def to_markdown(title: str, sections: list[tuple[str, list[str]]]) -> str:
    lines = [f"# {title}", ""]
    for heading, bullets in sections:
        lines.append(f"## {heading}")
        lines += [f"- {b}" for b in bullets] or ["- none"]
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def to_slack(title: str, sections: list[tuple[str, list[str]]]) -> list[dict]:
    """Minimal Block Kit: header + one section per heading."""
    blocks: list[dict] = [
        {"type": "header",
         "text": {"type": "plain_text", "text": title[:150]}}
    ]
    for heading, bullets in sections:
        text = f"*{heading}*\n" + "\n".join(f"• {b}" for b in bullets[:10])
        blocks.append({"type": "section",
                       "text": {"type": "mrkdwn", "text": text[:3000]}})
    return blocks
