# Feed Status

A record of how each health-monitoring source is pulled. To refresh, run
`src/audit_feeds.py`. All sources currently return items.

## Native RSS feeds

These pull directly from the source's own RSS/Atom feed and include dates.

- **International and multinational:** WHO, UN News (Health), Commonwealth
- **UK and EU government:** DHSC, NHS England, No 10 Downing Street, European Parliament News, European Commission
- **Think tanks:** Institute of Development Studies, Chatham House
- **International health orgs:** Unitaid, Pandemic Action Network, Global Sepsis Alliance, The Global Fund
- **Academic:** LSHTM, The Lancet
- **Media:** Health Policy Watch, Guardian Global Development, BBC Health

Two native feed URLs that took some finding:

- Chatham House: `https://www.chathamhouse.org/path/whatsnew.xml`
- The Global Fund: `https://www.theglobalfund.org/data/rss-feeds/news-releases/`

## Pulled via Google News

These sources have no usable native RSS (they block automated requests, render the
feed page in JavaScript, or only offer newsletters), so they are pulled through Google
News search feeds instead — `https://news.google.com/rss/search?q=...`. Google News
emits a proper dated feed for any query, which sidesteps the blocking.

- **International and multinational:** OECD, World Bank, UNDP, UNICEF
- **G20 and G7:** G20 (US presidency 2026), G7 (France presidency 2026)
- **Think tanks:** The Health Foundation, Nuffield Trust, Overseas Development Institute, Center for Global Development
- **International health orgs:** Gates Foundation, Bloomberg Philanthropies, Grand Challenges Canada, Wellcome Trust, PATH, MMV, NCD Alliance
- **Academic:** The BMJ, Imperial College
- **Media:** EURACTIV Health, Devex

Trade-offs to be aware of:

- Google News returns *coverage about* the org from many outlets, not just the org's own
  releases, so these feeds are noisier and higher-volume. The triage step is what keeps
  the briefing clean.
- The same story can appear across several of these feeds, so duplicates are possible
  until deduplication is added.
- Links route through `news.google.com` redirects rather than straight to the source.

EURACTIV Health was originally a native feed but began returning 403 (blocked), so it was
moved to Google News for reliability.

## Not separately tracked

The individual G20/G7 engagement groups (B20, T20, S20, W20, B7, T7, C7, S7, W7, Y7) run on
rotating host-country sites with no stable feeds. Their major announcements are generally
picked up by the G20/G7 and media feeds above.

## How the audit reads

`src/audit_feeds.py` parses each feed and reports the item count, HTTP status, and whether
the response was valid XML:

- zero items, status 404 — the URL is wrong, or the site blocks bots with a 404
- zero items, status 403 — the site blocked the request
- zero items, status 200 but an XML error — the URL returns a web page, not a feed
