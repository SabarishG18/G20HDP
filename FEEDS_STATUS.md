# Feed Status

A record of which health-monitoring sources have a working RSS feed and which don't.
To refresh, run `src/audit_feeds.py` (it needs the browser User-Agent set in `fetch.py`).

## Working (20)

These all pull cleanly and include dates.

- **International and multinational:** WHO, UN News (Health), Commonwealth
- **UK and EU government:** DHSC, NHS England, No 10 Downing Street, European Parliament News, European Commission
- **Think tanks:** Institute of Development Studies, Chatham House
- **International health orgs:** Unitaid, Pandemic Action Network, Global Sepsis Alliance, The Global Fund
- **Academic:** LSHTM, The Lancet
- **Media:** Health Policy Watch, Guardian Global Development, EURACTIV Health, BBC Health

Two feed URLs that took some finding:

- Chatham House: `https://www.chathamhouse.org/path/whatsnew.xml`
- The Global Fund: `https://www.theglobalfund.org/data/rss-feeds/news-releases/`

## Not working

**Blocks automated requests.** The feed (or site) rejects non-browser requests even
with a User-Agent set — some return 403, some return 404 to bots. Would need browser-style
scraping. Not pursued.

- OECD, The Health Foundation, The BMJ, Center for Global Development

**JavaScript-only.** The feed page renders in the browser with no static feed URL.

- MMV

**No public feed found.** Moved to newsletters or social media. UNDP and UNICEF news is
still picked up by the UN News feed above, so the gap is covered.

- UNDP, UNICEF, Nuffield Trust, ODI, Wellcome Trust, Devex, World Bank, Imperial College, PATH, NCD Alliance

## No feeds by nature

The G20 and G7 engagement groups (G20, B20, T20, S20, W20, G7, B7, T7, C7, S7, W7, Y7)
run on rotating host-country sites with no stable feeds. Monitor these by hand; their
main announcements are usually picked up by the media feeds above.

## If a blocked source ever becomes important

Options, easiest first:

1. **Add more browser headers** (`Accept`, `Referer`) to the request. May unblock simple
   403s; won't beat Cloudflare-style blocks.
2. **Use Google News as a proxy.** Google News publishes RSS for any query, including a
   site filter, e.g. `https://news.google.com/rss/search?q=site:bmj.com+when:7d`. This
   pulls a source's recent items through Google's index and sidesteps the site's blocking.
   Trade-offs: slight delay, links route via Google, not exhaustive.
3. **Headless browser** (e.g. Playwright) to render JavaScript pages and pass bot checks.
   Most capable, but slow and higher-maintenance — only if it's really needed.

## How the audit reads

`src/audit_feeds.py` parses each feed and reports the item count, HTTP status, and
whether the response was valid XML:

- zero items, status 404 — the URL is wrong, or the site blocks bots with a 404
- zero items, status 403 — the site blocked the request
- zero items, status 200 but an XML error — the URL returns a web page, not a feed
