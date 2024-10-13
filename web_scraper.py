import trafilatura
import logging
from requests.exceptions import RequestException

logger = logging.getLogger(__name__)

def get_website_text_content(url: str) -> str:
    """
    This function takes a url and returns the main text content of the website.
    The text content is extracted using trafilatura and easier to understand.
    """
    try:
        # Send a request to the website
        downloaded = trafilatura.fetch_url(url)
        if downloaded is None:
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
