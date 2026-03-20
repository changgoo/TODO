#!/usr/bin/env python3
"""SFIR seminar email reminder script.

Usage:
  python scripts/sfir_email.py --mode speaker   # 7-day advance notice to speaker
  python scripts/sfir_email.py --mode speaker --speaker "Krumholz"  # target a specific speaker
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
    with open(os.path.join(REPO_ROOT, "SFIR", "SFIR.json")) as f:
        return json.load(f)


def all_talks(schedule):
    for semester in schedule["semesters"]:
        yield from semester["talks"]


def find_talk(schedule, target_date):
    for talk in all_talks(schedule):
        if talk.get("date") == target_date.isoformat():
            return talk
    return None


def find_talk_by_speaker(schedule, name):
    """Find talks matching a speaker name (case-insensitive, partial match).

    Matches against first name, last name, or full name.
    Returns all matching talks sorted by date (future talks first).
    """
    name_lower = name.lower()
    matches = []
    for talk in all_talks(schedule):
        speaker = talk.get("speaker") or ""
        if not speaker:
            continue
        speaker_lower = speaker.lower()
        parts = speaker_lower.split()
        if name_lower == speaker_lower or name_lower in parts:
            matches.append(talk)
    matches.sort(key=lambda t: t.get("date", ""))
    return matches


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


def send_email(to_email, subject, body, cc_emails=None):
    api_key = os.environ["SENDGRID_API_KEY"]
    personalization = {"to": [{"email": to_email}]}
    if cc_emails:
        personalization["cc"] = [{"email": e} for e in cc_emails]
    payload = {
        "personalizations": [personalization],
        "from": {"email": FROM_EMAIL, "name": FROM_NAME},
        "subject": subject,
        "content": [{"type": "text/plain", "value": body}],
        "tracking_settings": {
            "click_tracking": {"enable": False, "enable_text": False},
        },
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
    parser.add_argument("--speaker", type=str, default=None,
                        help="Speaker name to target (first, last, or full; case-insensitive). "
                             "Only used with --mode speaker.")
    parser.add_argument("--dry-run", action="store_true", help="Print email without sending")
    args = parser.parse_args()

    if args.speaker and args.mode != "speaker":
        parser.error("--speaker can only be used with --mode speaker")

    today = datetime.now(TZ).date()
    schedule = load_schedule()
    templates = os.path.join(REPO_ROOT, "SFIR", "email_templates")

    if args.mode == "speaker":
        if args.speaker:
            matches = find_talk_by_speaker(schedule, args.speaker)
            if not matches:
                print(f"No speaker matching '{args.speaker}' found in schedule.")
                return
            if len(matches) > 1:
                print(f"Multiple talks found for '{args.speaker}':")
                for m in matches:
                    print(f"  {m['date']} — {m['speaker']}")
                # Use the next upcoming talk (or latest if all past)
                future = [m for m in matches if m["date"] >= today.isoformat()]
                talk = future[0] if future else matches[-1]
                print(f"Using: {talk['date']} — {talk['speaker']}")
            else:
                talk = matches[0]
        else:
            target = today + timedelta(days=7)
            talk = find_talk(schedule, target)
            if not talk or not talk.get("speaker"):
                print(f"No speaker set for {target}, skipping.")
                return
        to_email = talk.get("email")
        if not to_email:
            target = talk.get("date", "unknown date")
            notify_missing(
                f"Missing email for {talk['speaker']} ({target})",
                f"{talk['speaker']}'s talk is on {target} but no email address "
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
            print(f"No speaker set for Monday {target}, skipping.")
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
            print(f"No speaker set for today ({today}), skipping.")
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
    cc_emails = [FROM_EMAIL]
    if args.mode in ("friday", "dayof") and talk.get("email"):
        cc_emails.append(talk["email"])

    if args.dry_run:
        print(f"To:      {to_email}")
        print(f"CC:      {', '.join(cc_emails)}")
        print(f"Subject: {subject}")
        print("─" * 60)
        print(body)
        return

    send_email(to_email, subject, body, cc_emails=cc_emails)


if __name__ == "__main__":
    main()
