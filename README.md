# G20HDP
# Daily Health Monitoring

An automated daily news briefing for the G20 & G7 Health and Development Partnership.
It pulls health-policy news from a set of RSS feeds, filters to the last 24 hours,
uses an LLM to judge each item's relevance and write a short summary, and emails a
grouped briefing each morning.

## What it does

1. **Fetch** the latest items from ~20 health-policy RSS feeds (`config.yaml`).
2. **Filter** to articles published in the last 24 hours.
3. **Triage** each item with an LLM into ACCEPT / REJECT / UNSURE based on relevance
   to the Partnership's mission (global and UK health, health financing, health systems,
   pandemics, AMR, NCDs, the SDGs).
4. **Summarise** the accepted and unsure items in 2–3 sentences, in house style.
5. **Deliver** the result as an HTML email (summaries in the body, links to sources)
   with a Word document attached. Rejected items are left out of the email but logged
   to the console for review.

## Project structure

    src/
      fetch.py        # read an RSS/Atom feed
      filter.py       # keep only the last 24 hours
      summarise.py    # LLM calls: classify() for triage, summarise() for synopses
      build_doc.py    # render the Word document and the HTML email body
      deliver.py      # send the email via Gmail
      main.py         # orchestrates the whole run
      audit_feeds.py  # one-off tool to check which feeds work
    config.yaml       # the list of sources (name, url, section)
    FEEDS_STATUS.md   # which feeds work, which don't, and why
    requirements.txt

## Setup

1. Clone the repo and create a virtual environment:

       python3 -m venv .venv
       source .venv/bin/activate        # Windows: .venv\Scripts\activate
       pip install -r requirements.txt

2. Create a `.env` file in the project root (never committed):

       OPENAI_API_KEY=sk-...
       GMAIL_ADDRESS=youraddress@gmail.com
       GMAIL_APP_PASSWORD=your16charapppassword
       RECIPIENTS=person1@example.com,person2@example.com

   The Gmail value is a Google **app password** (requires 2-Step Verification on the
   account), not the normal login password.

## Running

    python3 src/main.py

This fetches, triages, summarises, writes a dated `.docx` to `output/`, and emails it.
To check feed health at any time:

    python3 src/audit_feeds.py

## Configuration

Sources live in `config.yaml`. Each has a `name`, `url`, and `section`. Adding a source
is just adding a few lines; the audit script (`audit_feeds.py`) confirms whether a feed
works. See `FEEDS_STATUS.md` for the current state of every source and the reasoning
behind the ones that don't work.

The relevance rubric lives in `CLASSIFY_PROMPT` inside `summarise.py` — edit it to widen
or narrow what counts as relevant.

## Deployment

Designed to run on a schedule via GitHub Actions (daily, plus a manual "Run workflow"
button for on-demand runs). The `.env` values are stored as GitHub repository secrets
rather than committed. For handover, the API key and email account should belong to the
organisation so the tool keeps running independently.

## Roadmap

- **Business sources (Phase 2):** extend `config.yaml` with parliamentary and financial
  sources (gov.uk department feeds, committees, regulators). Triage already handles
  relevance, so no rework is needed — items just need a `Business` category tag.
- **Deduplication:** track seen articles to avoid repeats and handle missed runs.
- **Comparative deep-dive:** an optional agentic summary of a few top stories.
