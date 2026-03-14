#!/usr/bin/env python3
"""SFIR seminar email reminder script.

Usage:
  python scripts/sfir_email.py --mode speaker   # 7-day advance notice to speaker
  python scripts/sfir_email.py --mode friday    # Friday announcement to sfir@
  python scripts/sfir_email.py --mode dayof     # 1-hour-before reminder to sfir@
  python scripts/sfir_email.py --mode speaker --dry-run   # print without sending
"""

import argparse
import json
import os
import urllib.request
import urllib.error
from datetime import date, datetime, timedelta
import zoneinfo

FROM_EMAIL = "changgoo@princeton.edu"
FROM_NAME = "SFIR Seminar"
SFIR_LIST = "sfir@princeton.edu"
TZ = zoneinfo.ZoneInfo("America/New_York")

REPO_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")


def load_schedule():
    with open(os.path.join(REPO_ROOT, "SFIR.json")) as f:
        return json.load(f)


def all_talks(schedule):
    for semester in schedule["semesters"]:
        yield from semester["talks"]


def find_talk(schedule, target_date):
    for talk in all_talks(schedule):
        if talk.get("date") == target_date.isoformat():
            return talk
    return None


def render_template(template_path, talk, schedule):
    """Return (subject, body) with placeholders substituted."""
    with open(template_path) as f:
        raw = f.read()

    # Split frontmatter
    subject = ""
    body = raw
    if raw.startswith("---"):
        _, fm, body = raw.split("---", 2)
        for line in fm.splitlines():
            if line.startswith("subject:"):
                subject = line.split("subject:", 1)[1].strip().strip('"')

    body = body.strip()
    speaker = talk.get("speaker") or ""
    affiliation = talk.get("affiliation") or ""
    label = talk.get("label") or ""
    date_short = label.replace("Monday, ", "")

    subs = {
        "{{speaker_name}}": speaker,
        "{{affiliation}}": affiliation,
        "{{speaker_email}}": talk.get("email") or "",
        "{{host_name}}": talk.get("host") or "Chang-Goo Kim",
        "{{title}}": talk.get("title") or "TBD",
        "{{abstract}}": talk.get("abstract") or "TBD",
        "{{date}}": talk.get("date") or "",
        "{{date_short}}": date_short,
        "{{label}}": label,
        "{{time}}": talk.get("time") or "4:00 PM",
        "{{location}}": talk.get("location") or "Dome Room",
        "{{coordinator_name}}": schedule["coordinator"]["name"],
        "{{coordinator_email}}": schedule["coordinator"]["email"],
    }

    for k, v in subs.items():
        subject = subject.replace(k, v)
        body = body.replace(k, v)

    return subject, body


def send_email(to_email, subject, body):
    api_key = os.environ["SENDGRID_API_KEY"]
    payload = {
        "personalizations": [{"to": [{"email": to_email}]}],
        "from": {"email": FROM_EMAIL, "name": FROM_NAME},
        "subject": subject,
        "content": [{"type": "text/plain", "value": body}],
    }
    req = urllib.request.Request(
        "https://api.sendgrid.com/v3/mail/send",
        data=json.dumps(payload).encode(),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req) as resp:
            print(f"Sent to {to_email} — status {resp.status}")
    except urllib.error.HTTPError as e:
        print(f"SendGrid error {e.code}: {e.read().decode()}")
        raise


def notify_missing(subject, message, dry_run=False):
    """Send a warning email to the organizer about missing info."""
    print(f"WARNING: {message}")
    if dry_run:
        print(f"[dry-run] Would notify {FROM_EMAIL}: {subject}")
        return
    send_email(FROM_EMAIL, f"[SFIR] {subject}", message)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["speaker", "friday", "dayof"], required=True)
    parser.add_argument("--dry-run", action="store_true", help="Print email without sending")
    args = parser.parse_args()

    today = datetime.now(TZ).date()
    schedule = load_schedule()
    templates = os.path.join(REPO_ROOT, "email_templates")

    if args.mode == "speaker":
        target = today + timedelta(days=7)
        talk = find_talk(schedule, target)
        if not talk or not talk.get("speaker"):
            notify_missing(
                f"No speaker set for {target}",
                f"The SFIR talk on {target} has no speaker assigned in SFIR.json. "
                f"Please update the schedule.",
                args.dry_run,
            )
            return
        to_email = talk.get("email")
        if not to_email:
            notify_missing(
                f"Missing email for {talk['speaker']} ({target})",
                f"{talk['speaker']}'s talk is in 7 days ({target}) but no email address "
                f"is set in SFIR.json. Please add it so the reminder can be sent.",
                args.dry_run,
            )
            return
        if talk.get("title") and talk.get("abstract"):
            print(f"Talk info already received from {talk['speaker']}, skipping.")
            return
        template = os.path.join(templates, "speaker_reminder.md")

    elif args.mode == "friday":
        # Friday → next Monday is +3 days
        target = today + timedelta(days=3)
        talk = find_talk(schedule, target)
        if not talk or not talk.get("speaker"):
            notify_missing(
                f"No speaker set for Monday {target}",
                f"The SFIR talk on {target} has no speaker assigned in SFIR.json. "
                f"Friday announcement was not sent.",
                args.dry_run,
            )
            return
        if not talk.get("title") or not talk.get("abstract"):
            notify_missing(
                f"Missing title/abstract for {talk['speaker']} ({target})",
                f"{talk['speaker']}'s talk is on Monday ({target}) but title or abstract "
                f"is still missing in SFIR.json. Friday announcement was sent with 'TBD'.",
                args.dry_run,
            )
        to_email = SFIR_LIST
        template = os.path.join(templates, "friday_announcement.md")

    elif args.mode == "dayof":
        talk = find_talk(schedule, today)
        if not talk or not talk.get("speaker"):
            notify_missing(
                f"No speaker set for today ({today})",
                f"The SFIR talk today ({today}) has no speaker assigned in SFIR.json. "
                f"Day-of reminder was not sent.",
                args.dry_run,
            )
            return
        if not talk.get("title") or not talk.get("abstract"):
            notify_missing(
                f"Missing title/abstract for {talk['speaker']} (today)",
                f"{talk['speaker']}'s talk is today ({today}) but title or abstract "
                f"is still missing in SFIR.json. Day-of reminder was sent with 'TBD'.",
                args.dry_run,
            )
        to_email = SFIR_LIST
        template = os.path.join(templates, "day_of_reminder.md")

    subject, body = render_template(template, talk, schedule)

    if args.dry_run:
        print(f"To:      {to_email}")
        print(f"Subject: {subject}")
        print("─" * 60)
        print(body)
        return

    send_email(to_email, subject, body)


if __name__ == "__main__":
    main()
