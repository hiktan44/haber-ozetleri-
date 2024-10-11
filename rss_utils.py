import feedparser

def fetch_rss_feeds(url):
    """
    Fetch and parse RSS feed items from the given URL.
    """
    feed = feedparser.parse(url)
    items = []
    for entry in feed.entries:
        item = {
            'title': entry.get('title', ''),
            'link': entry.get('link', ''),
            'published': entry.get('published', '')
        }
        items.append(item)
    return items
