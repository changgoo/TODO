#!/usr/bin/env python3
"""Generate SFIR.md from SFIR.json."""

import json
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
JSON_PATH = SCRIPT_DIR / "SFIR.json"
MD_PATH = SCRIPT_DIR / "SFIR.md"


def format_date(date_str):
    """Format date as 'Mon, Jan 1'."""
    d = datetime.strptime(date_str, "%Y-%m-%d")
    return d.strftime("%a, %b %-d")


def format_speaker(talk):
    speaker = talk.get("speaker")
    if not speaker:
        return "—"
    affiliation = talk.get("affiliation")
    return f"{speaker} ({affiliation})" if affiliation else speaker


def format_host(talk):
    return talk.get("host") or "—"


def format_title_and_notes(talk, default_location):
    """Return (title_cell, notes_cell)."""
    title = talk.get("title")
    notes = talk.get("notes") or ""
    location = talk.get("location")

    notes_parts = []
    cancelled = "cancelled" in notes.lower()

    if cancelled:
        # Strip "— cancelled" suffix, keep the rest as a note
        notes_clean = notes.lower().replace("— cancelled", "").replace("—cancelled", "")
        # Restore original casing by trimming the original string
        trim_len = len(notes) - len(notes.rstrip().rstrip("cancelled").rstrip("— ").rstrip())
        notes_clean = notes[: len(notes) - trim_len].strip().rstrip("—").strip()
        if notes_clean:
            notes_parts.append(notes_clean)
    elif notes:
        notes_parts.append(notes)

    # Suppress location if it matches the default (allow "Dome Room" to match "Dome Room, Peyton Hall")
    if location and not default_location.startswith(location):
        notes_parts.append(location)

    notes_cell = "; ".join(notes_parts)
    title_cell = "~~cancelled~~" if cancelled else (title or "—")

    return title_cell, notes_cell


def semester_default_time(semester):
    """Infer the most common talk time in a semester."""
    times = [t["time"] for t in semester["talks"] if t.get("time")]
    return max(set(times), key=times.count) if times else None


def generate_md(data):
    lines = []
    default_location = data["default_location"]

    # Header
    lines.append(f"# {data['title']} 2025–2026")
    lines.append("")
    lines.append(f"- **Location:** {default_location} (unless noted)")
    lines.append(f"- **Time:** {data['default_time']} (unless noted)")
    lines.append(f"- **Zoom:** {data['zoom']}")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Semesters in reverse chronological order (newest first)
    for semester in reversed(data["semesters"]):
        sem_time = semester_default_time(semester)
        header = f"## {semester['name']}"
        if sem_time and sem_time != data["default_time"]:
            header += f" ({sem_time})"
        lines.append(header)
        lines.append("")
        lines.append("| Date | Speaker | Host | Talk Title | Notes |")
        lines.append("|------|---------|------|-----------|-------|")

        for talk in semester["talks"]:
            date = format_date(talk["date"])
            speaker = format_speaker(talk)
            host = format_host(talk)
            title_cell, notes_cell = format_title_and_notes(talk, default_location)
            lines.append(f"| {date} | {speaker} | {host} | {title_cell} | {notes_cell} |")

        lines.append("")
        lines.append("---")
        lines.append("")

    coord = data["coordinator"]
    lines.append(f"*Email coordinator: {coord['name']} <{coord['email']}>*")

    return "\n".join(lines) + "\n"


def main():
    with open(JSON_PATH) as f:
        data = json.load(f)

    content = generate_md(data)
    MD_PATH.write_text(content)
    print(f"Generated {MD_PATH}")


if __name__ == "__main__":
    main()
