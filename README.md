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

1. Clone the repo and create a virtual
