# Automate the Boring Stuff — Plus

An extension from *Automate the Boring Stuff with Python* (Al
Sweigart). The book's exercises are solid but deliberately minimal — this repo
takes them a bit further: adding persistence, better ergonomics, and eventually
LLM/agent integration where it actually adds value (not just for the sake of
it).

## Why this exists

The book's projects are throwaway scripts by design — that's the point, they
teach the concepts fast. This repo is what happens when you don't throw them
away: give the password locker real storage instead of a hardcoded dict, let
the XKCD downloader resume from where it left off, let an agent decide what
to scrape instead of hardcoding a CSS selector. Some projects stay close to
the original; some barely resemble it anymore.

## Structure

```
projects/
├── 06.db/
│   ├── pw.py
│   ├── tilt.py
├── 09.multiclipboard/
├── 11.xkcd_downloader/
└── ...
shared/
└── llm_utils.py             # common wrapper(s) for LLM calls, used across projects
requirements.txt
.gitignore
```

Each project folder is self-contained and has its own `README.md` explaining:

1. What the book's version does
2. What this version changes and why
3. (Where applicable) how/why an LLM or agent is involved

Numbering follows the book's chapter numbers loosely, just to keep things
findable — it's not meant to imply you need to go in order.

## Principles:

- **Persistence over one-shot scripts.** SQLite instead of in-memory dicts,
  state files instead of "just run it again by hand."
- **No security theater.** If something is genuinely insecure (like a
  password locker with no real encryption), the README says so plainly
  instead of pretending otherwise.
- **LLMs/agents where they replace judgment, not where they replace typing.**
  The interesting version of "regex generator" is an agent that explains
  *why* it wrote a given pattern, not just a script that calls an API and
  prints a regex.
- **Secrets never get committed.** API keys and local DB files are
  gitignored from day one.

## Setup

```bash
git clone <repo-url>
cd automate
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Each project's own README will note any extra setup (e.g. an `.env` file
with an API key) if it needs one.

## Status

Work in progress — projects get added/reworked as I go through the book
again. See individual project READMEs for what's actually implemented vs.
planned.

## Credit

Original exercises and book: *Automate the Boring Stuff with Python* by Al
Sweigart (No Starch Press), released under a Creative Commons
Attribution-NonCommercial-ShareAlike license. This repo contains original
code inspired by / extending those exercises, not the book's own source
code.