import trafilatura
import logging
from requests.exceptions import RequestException
import requests

logger = logging.getLogger(__name__)

def get_website_text_content(url: str) -> str:
    """
    This function takes a url and returns the main text content of the website.
    The text content is extracted using trafilatura and easier to understand.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        # Send a request to the website
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        downloaded = response.text
        if not downloaded:
            logger.error(f"Failed to download content from {url}")
            return None
        
        text = trafilatura.extract(downloaded)
        if text is None:
            logger.error(f"Failed to extract text content from {url}")
            return None
        
        return text
    except RequestException as e:
        logger.error(f"Network error while fetching content from {url}: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error fetching content from {url}: {str(e)}")
        return None
