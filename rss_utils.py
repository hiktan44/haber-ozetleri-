import feedparser
import logging

logger = logging.getLogger(__name__)

def fetch_rss_feeds(url):
    """
    Fetch and parse RSS feed items from the given URL.
    """
    try:
        feed = feedparser.parse(url)
        
        if feed.bozo:
            logger.error(f"Error parsing RSS feed from {url}: {feed.bozo_exception}")
            return None
        
        items = []
        for entry in feed.entries:
            item = {
                'title': entry.get('title', ''),
                'link': entry.get('link', ''),
                'published': entry.get('published', '')
            }
            items.append(item)
        
        if not items:
            logger.warning(f"No items found in the RSS feed from {url}")
        
        return items
    except Exception as e:
        logger.error(f"Error fetching RSS feed from {url}: {str(e)}")
        return None
