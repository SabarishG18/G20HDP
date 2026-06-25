import feedparser

WHO_FEED = "https://www.who.int/rss-feeds/news-english.xml"

USER_AGENT = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
              "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36")

def get_entries(feed_url):
    
    feed = feedparser.parse(feed_url, agent=USER_AGENT)
    return feed.entries  


if __name__ == "__main__":

    entries = get_entries(WHO_FEED)

    print(f"Found {len(entries)} items")

    for entry in entries[:10]:
        print(entry.title)
        print(entry.link)
        print()


    
