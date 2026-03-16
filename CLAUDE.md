# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Purpose

This repository is a personal productivity and task management system for an astrophysics researcher. It uses a Eisenhower Matrix (Q1–Q4 urgency/importance quadrants) to organize work.

## Architecture

**Source of truth: GitHub Issue #1**
The canonical task list lives in GitHub Issue #1 (`changgoo/TODO`), not in `README.md`. The README is a local mirror that should be kept in sync. Always update the GitHub issue when modifying tasks, and push README changes to the remote.

**Components:**
- `README.md` — Local mirror of the task list (Eisenhower Matrix format, Q1–Q4 quadrants + Completed section)
- `.github/workflows/daily-reminder.yml` — GitHub Action that runs weekdays at 11 AM EDT; fetches Q1+Q2 todos from Issue #1 via `gh api` and emails them via SendGrid
- `populate-reminders.applescript` — One-time script to seed macOS Reminders app with tasks; run via `osascript populate-reminders.applescript` or Script Editor
- `SFIR.json` — Structured schedule for the Star Formation/ISM Rendezvous (SFIR) seminar (Fall 2025 + Spring 2026); source of truth for email automation
- `SFIR.md` — Human-readable markdown mirror of `SFIR.json`
- `scripts/sfir_email.py` — Sends seminar reminder emails via SendGrid; run with `--mode speaker|friday|dayof`; supports `--dry-run`
- `email_templates/` — Three email templates: `speaker_reminder.md`, `friday_announcement.md`, `day_of_reminder.md`
- `.github/workflows/sfir-speaker-reminder.yml` — Daily cron (9 AM ET); emails speaker 7 days before talk to request title/abstract
- `.github/workflows/sfir-friday-announcement.yml` — Friday cron (9 AM ET); emails sfir@princeton.edu with next Monday's talk
- `.github/workflows/sfir-day-of-reminder.yml` — Monday cron (2 PM ET); emails sfir@princeton.edu 1 hour before talk (Spring talks at 3 PM)

## Workflow

**Updating tasks:**
1. Edit `README.md` locally (check/uncheck boxes, add/move tasks)
2. Push to remote — the GitHub Action reads from Issue #1, so also update Issue #1 to keep the email reminder accurate

**Daily email reminder:**
- Triggered automatically on weekdays (cron) or manually via GitHub Actions `workflow_dispatch`
- Requires repo secrets: `SENDGRID_API_KEY`, `SENDGRID_TO_EMAIL`
- Reads unchecked top-level items from Q1 and Q2 sections of Issue #1 body

**SFIR seminar email automation:**
- All emails sent from `changgoo@princeton.edu` via SendGrid (requires `SENDGRID_API_KEY`)
- Update `SFIR.json` when speaker info (email, title, abstract) is confirmed
- Speaker reminder skips if: no email set, or title+abstract already filled
- Friday/day-of reminders send with "TBD" if title/abstract missing, and notify `changgoo@princeton.edu`
- No speaker set → silently skip all reminders for that week

**Task format conventions:**
- Top-level tasks: `- [ ] **Task name**`
- Subtasks: indented `    - [ ] subtask`
- Completed items move to the `## Completed` section with a date note
- Section headers must match exactly: `## Q1`, `## Q2`, `## Q3`, `## Q4`, `## Completed` (the email parser depends on this)
