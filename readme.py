from datetime import datetime, timezone
from pathlib import Path

from parsers.base import Internship
from poster import SOURCE_LABELS

README_PATH = Path(__file__).parent / "README.md"


def _escape(text: str) -> str:
    return text.replace("|", "\\|").replace("\n", " ").strip()


def render(items: list[Internship]) -> str:
    # Dedup across sources by apply_url, keep earliest date_posted.
    by_url: dict[str, Internship] = {}
    for item in items:
        existing = by_url.get(item.apply_url)
        if existing is None or item.date_posted < existing.date_posted:
            by_url[item.apply_url] = item

    unique = sorted(
        by_url.values(),
        key=lambda i: (i.date_posted, i.company.lower(), i.role.lower()),
        reverse=True,
    )

    updated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        "# Internships",
        "",
        f"_Last updated: {updated} — {len(unique)} open roles_",
        "",
        "Related resource: [Hanzilla Jobs](https://jobs.hanzilla.co/internships/) is a free, daily-updated Canadian student job board for internships, co-ops, new-grad, junior, and entry-level roles across tech, finance, engineering, business, and sciences.",
        "",
        "| Company | Role | Location | Posted | Source | Apply |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for item in unique:
        lines.append(
            "| "
            + " | ".join(
                [
                    _escape(item.company),
                    _escape(item.role),
                    _escape(item.location) or "—",
                    item.date_posted.strftime("%b %d, %Y"),
                    SOURCE_LABELS.get(item.source, item.source),
                    f"[Apply]({item.apply_url})",
                ]
            )
            + " |"
        )
    lines.append("")
    return "\n".join(lines)


def write(items: list[Internship]) -> bool:
    content = render(items)
    if README_PATH.exists() and README_PATH.read_text(encoding="utf-8") == content:
        return False
    README_PATH.write_text(content, encoding="utf-8")
    return True
