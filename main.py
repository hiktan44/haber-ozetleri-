import streamlit as st
import logging
import json
import os
from rss_utils import fetch_rss_feeds
from web_scraper import get_website_text_content
from summarizer import summarize_text
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set page title and layout
st.set_page_config(page_title="RSS Feed Summary Generator", layout="wide")

def load_feeds():
    if os.path.exists('feeds.json'):
        with open('feeds.json', 'r') as f:
            return json.load(f)
    return []

def save_feeds():
    with open('feeds.json', 'w') as f:
        json.dump(st.session_state.feeds, f)

# Initialize session state for feeds
if 'feeds' not in st.session_state:
    st.session_state.feeds = load_feeds()

# Function to add feed
def add_feed(url):
    if url not in st.session_state.feeds:
        st.session_state.feeds.append(url)
        save_feeds()

# Function to remove feed
def remove_feed(url):
    st.session_state.feeds.remove(url)
    save_feeds()

# Title
st.title("RSS Feed Summary Generator")
st.markdown("This app fetches RSS feeds, summarizes their content, and displays the results.")

# Input for new RSS feed URL
new_feed = st.text_input("Enter a new RSS feed URL:")
if st.button("Add Feed"):
    if new_feed:
        add_feed(new_feed)
        st.success(f"Added feed: {new_feed}")
        save_feeds()
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
            save_feeds()
            st.rerun()

# Add summary length slider
summary_length = st.slider("Summary Length (number of sentences)", min_value=1, max_value=10, value=3)

# Fetch and summarize feeds
if st.button("Fetch and Summarize Feeds"):
    if st.session_state.feeds:
        for feed_url in st.session_state.feeds:
            st.subheader(f"Feed: {feed_url}")
            feed_items = fetch_rss_feeds(feed_url)
            
            if feed_items is None:
                st.error(f"Failed to fetch RSS feed from {feed_url}. The feed might be inaccessible, have an invalid format, or require authentication. Please check the URL and try again.")
                continue
            
            if not feed_items:
                st.warning(f"No items found in the RSS feed from {feed_url}")
                continue
            
            for item in feed_items[:10]:  # Process first 10 items
                try:
                    published_date = datetime.strptime(item['published'], '%a, %d %b %Y %H:%M:%S %z').strftime('%Y-%m-%d %H:%M:%S')
                except ValueError:
                    try:
                        published_date = datetime.strptime(item['published'], '%Y-%m-%dT%H:%M:%S%z').strftime('%Y-%m-%d %H:%M:%S')
                    except ValueError:
                        published_date = item['published']
                
                with st.expander(f"**{item['title']}** (Published: {published_date})"):
                    st.write(f"Link: {item['link']}")
                    
                    # Fetch and summarize content
                    logger.info(f"Attempting to summarize content from: {item['link']}")
                    content = get_website_text_content(item['link'])
                    if content:
                        summary = summarize_text(content, num_sentences=summary_length)
                        if summary.startswith("Error:"):
                            st.error(f"Error during summarization: {summary}")
                        else:
                            logger.info(f"Summary generated: {summary[:100]}...")  # Log first 100 chars of summary
                            st.write("Summary:")
                            st.write(summary)
                    else:
                        st.error(f"Unable to fetch or summarize content from: {item['link']}. The page might be inaccessible, have restricted content, or require authentication.")
    else:
        st.warning("No feeds available. Please add some RSS feed URLs.")

# Add some spacing at the bottom
st.markdown("<br><br>", unsafe_allow_html=True)
