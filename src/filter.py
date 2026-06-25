from fetch import get_entries, WHO_FEED
import time
import calendar

def filter_recent(entries, hours=24):

    now = time.time()
    cutoff = now - (hours * 3600)
    keep_entries = []
    for entry in entries:

        # Some feeds (e.g. gov.uk Atom) use 'updated' instead of 'published',
        # and a few have no date at all. Try published first, fall back to
        # updated, and skip the entry entirely if neither exists.
        date_struct = entry.get("published_parsed") or entry.get("updated_parsed")
        if date_struct is None:
            continue
        published = calendar.timegm(date_struct)
        if published >= cutoff:
            keep_entries.append(entry)
    return keep_entries

if __name__ == "__main__":

    all_entries = get_entries(WHO_FEED)

    recent_articles = filter_recent(all_entries, hours=48)

    print(f"{len(recent_articles)} of {len(all_entries)} items are from the last 24h\n")
    for entry in recent_articles:
        print(entry.title)
