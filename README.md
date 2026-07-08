# G20HDP — Daily Health Monitoring

An automated daily news briefing for the G20 & G7 Health and Development Partnership. It
pulls health-policy news from around 60 sources, filters to the last 24 hours, removes
duplicates, uses an LLM to judge each item's relevance and write a short summary, and emails
a grouped briefing each morning.

## What it does

1. **Fetch** the latest items from ~60 sources listed in `config.yaml`. Sources with a native
   RSS/Atom feed are read directly; sources without one are pulled via Google News search feeds.
2. **Filter** to articles published in the last 24 hours.
3. **Deduplicate** — collapse the same story reported by several outlets into one entry, keeping
   the others as "also covered by" links.
4. **Triage** each item with an LLM into ACCEPT / REJECT / UNSURE, focused on high-level health
   policy, financing and systems (the Partnership's space) and skipping soft or consumer health news.
5. **Summarise** the accepted and unsure items in 2–4 sentences — what was announced, who is
   involved, and why it matters to the Partnership.
6. **Deliver** as an HTML email (summaries in the body, links to sources) with a Word document
   attached. Rejected items are left out of the email but logged to the console for review.

## Project structure

```
src/
  fetch.py        # read an RSS/Atom feed
  filter.py       # keep only the last 24 hours
  dedup.py        # collapse duplicate stories across sources
  summarise.py    # LLM calls: classify() for triage, summarise() for synopses
  build_doc.py    # render the Word document and the HTML email body
  deliver.py      # send the email via Gmail
  main.py         # orchestrates the whole run
  app.py          # optional Streamlit app: generate / view / download / email on demand
  audit_feeds.py  # tool to check which feeds are working
config.yaml       # the list of sources (name, url, section)
FEEDS_STATUS.md   # which feeds work, which don't, and why
requirements.txt
```

## Setup

1. Clone the repo and create a virtual environment:

   ```
   python3 -m venv .venv
   source .venv/bin/activate        # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. Create a `.env` file in the project root (never committed):

   ```
   OPENAI_API_KEY=sk-...
   GMAIL_ADDRESS=youraddress@gmail.com
   GMAIL_APP_PASSWORD=your16charapppassword
   RECIPIENTS=person1@example.com,person2@example.com
   ```

   The Gmail value is a Google app password (requires 2-Step Verification on the account),
   not the normal login password.

## Running

```
python3 src/main.py
```

This fetches, filters, dedupes, triages, summarises, writes a dated `.docx` to `output/`, and
emails it. Other entry points:

```
python3 src/audit_feeds.py     # check which feeds are returning items
streamlit run src/app.py       # optional web app to generate/view a briefing on demand
```

## Configuration

Sources live in `config.yaml`. Each has a `name`, `url`, and `section`. Adding a source is just
adding a few lines; `audit_feeds.py` confirms whether a feed returns items. Sources without a
usable native feed use a Google News search feed (with `when:2d` so only recent items come back).
See `FEEDS_STATUS.md` for the state of every source and the reasoning behind the ones that don't work.

The tuning knobs:

- `CLASSIFY_PROMPT` in `summarise.py` — the relevance rubric (what counts as ACCEPT/REJECT/UNSURE).
- `SUMMARISE_PROMPT` in `summarise.py` — the summary style.
- `threshold` in `dedup.py` — how aggressively duplicate stories are merged.

## Deployment

Designed to run on a schedule via GitHub Actions (daily, plus a manual "Run workflow" button for
on-demand runs). The `.env` values are stored as GitHub repository secrets rather than committed.
For handover, the API key and email account should belong to the organisation so the tool keeps
running independently. The Streamlit app can be hosted free on Streamlit Community Cloud using the
same secrets.

## Roadmap

- **Business sources (Phase 2):** extend `config.yaml` with parliamentary and financial sources
  (gov.uk departments, committees, regulators). Triage already handles relevance — just tag them
  with a `Business` section.
- **Semantic deduplication:** the current dedup matches on shared headline words; embeddings-based
  matching would also catch the same story written up with different headlines.
- **Email newsletter ingestion:** pull free newsletters (Devex Newswire, POLITICO Playbook) from
  the inbox to capture content that isn't in any feed.
- **Personalised emails:** per-user source toggles (via the Streamlit app), with one shared
  processing run so cost stays flat as users are added.
- **Monthly partner newsletter:** the same pipeline over a wider window, in an editorial format.
- **Comparative deep-dive:** an optional agentic summary of a few top stories.
