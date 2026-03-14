# Development Log

## 2026-03-13 — SFIR Seminar Email Automation

**Added files:**
- `SFIR.json` — Structured seminar schedule (Fall 2025 + Spring 2026) with fields: date, speaker, affiliation, email, host, title, abstract, location, time, notes
- `SFIR.md` — Human-readable markdown mirror of the schedule
- `SFIR Schedule - 2025-2026.csv` — Source CSV from Google Sheets
- `scripts/sfir_email.py` — Unified email script; run with `--mode speaker|friday|dayof`; supports `--dry-run`
- `email_templates/speaker_reminder.md` — Template for 7-day advance notice to speaker asking for title/abstract
- `email_templates/friday_announcement.md` — Template for Friday announcement to sfir@princeton.edu
- `email_templates/day_of_reminder.md` — Template for 1-hour-before reminder to sfir@princeton.edu
- `.github/workflows/sfir-speaker-reminder.yml` — Daily cron (9 AM ET); sends speaker reminder if a talk is 7 days out
- `.github/workflows/sfir-friday-announcement.yml` — Friday cron (9 AM ET); sends weekly announcement
- `.github/workflows/sfir-day-of-reminder.yml` — Monday cron (3 PM ET); sends day-of reminder 1 hour before 4 PM talks

**Required GitHub secret:** `SENDGRID_API_KEY` (already in use by `daily-reminder.yml`)

**Skip logic in `sfir_email.py`:**
- No speaker set → silently skip (no email)
- Speaker email missing → notify organizer (`changgoo@princeton.edu`) and skip
- Title+abstract already filled → skip (info already received, no need to re-ask speaker)
- Title/abstract missing on `friday`/`dayof` → notify organizer and still send announcement with "TBD"

**Notes:**
- All emails sent from `changgoo@princeton.edu` via SendGrid
- Spring 2026 talks are at 3 PM ET; day-of cron fires at 2 PM ET (1 hour before)
- Fall 2025 is complete; cron schedule is tuned for Spring 2026 onwards

---

## 2026-03-13 — Daily Q1/Q2 Reminder

- `.github/workflows/daily-reminder.yml` — Weekday cron (11 AM ET); fetches Q1+Q2 from GitHub Issue #1 and emails via SendGrid
