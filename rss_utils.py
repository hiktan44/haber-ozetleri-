import feedparser
import logging
from requests.exceptions import RequestException
import requests

logger = logging.getLogger(__name__)

def fetch_rss_feeds(url):
    """
    Fetch and parse RSS feed items from the given URL.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        feed = feedparser.parse(response.content)
        
        if feed.bozo:
            logger.error(f"Error parsing RSS feed from {url}: {feed.bozo_exception}")
            return None
        
        items = []
        for entry in feed.entries:
            item = {
                'title': entry.get('title', 'No title'),
                'link': entry.get('link', ''),
                'published': entry.get('published', entry.get('updated', 'No date'))
            }
            items.append(item)
        
        if not items:
            logger.warning(f"No items found in the RSS feed from {url}")
        
        return items
    except RequestException as e:
        logger.error(f"Network error while fetching RSS feed from {url}: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error fetching RSS feed from {url}: {str(e)}")
        return None
