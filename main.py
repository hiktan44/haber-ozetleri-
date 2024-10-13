import streamlit as st
import logging
from rss_utils import fetch_rss_feeds
from web_scraper import get_website_text_content
from summarizer import summarize_text

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set page title and layout
st.set_page_config(page_title="RSS Feed Summary Generator", layout="wide")

# Initialize session state for feeds
if 'feeds' not in st.session_state:
    st.session_state.feeds = []

# Function to add feed
def add_feed(url):
    if url not in st.session_state.feeds:
        st.session_state.feeds.append(url)

# Function to remove feed
def remove_feed(url):
    st.session_state.feeds.remove(url)

# Title
st.title("RSS Feed Summary Generator")

# Input for new RSS feed URL
new_feed = st.text_input("Enter a new RSS feed URL:")
if st.button("Add Feed"):
    if new_feed:
        add_feed(new_feed)
        st.success(f"Added feed: {new_feed}")
    else:
        st.warning("Please enter a valid URL.")

# Display and manage existing feeds
st.subheader("Existing Feeds")
for index, feed_url in enumerate(st.session_state.feeds):
    col1, col2 = st.columns([3, 1])
    with col1:
        st.text(feed_url)
    with col2:
        if st.button("Remove", key=f"remove_{index}"):
            remove_feed(feed_url)
            st.experimental_rerun()

# Fetch and summarize feeds
if st.button("Fetch and Summarize Feeds"):
    if st.session_state.feeds:
        for feed_url in st.session_state.feeds:
            st.subheader(f"Feed: {feed_url}")
            feed_items = fetch_rss_feeds(feed_url)
            
            for item in feed_items[:10]:  # Process first 10 items
                with st.expander(f"**{item['title']}**"):
                    st.write(f"Link: {item['link']}")
                    
                    # Fetch and summarize content
                    logger.info(f"Attempting to summarize content from: {item['link']}")
                    content = get_website_text_content(item['link'])
                    if content:
                        summary = summarize_text(content)
                        logger.info(f"Summary generated: {summary[:100]}...")  # Log first 100 chars of summary
                        st.write("Summary:")
                        st.write(summary)
                    else:
                        logger.warning(f"Unable to fetch or summarize content from: {item['link']}")
                        st.write("Unable to fetch or summarize content.")
    else:
        st.warning("No feeds available. Please add some RSS feed URLs.")

# Add some spacing at the bottom
st.markdown("<br><br>", unsafe_allow_html=True)
