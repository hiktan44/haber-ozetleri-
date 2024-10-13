import streamlit as st
import pandas as pd
from rss_utils import fetch_rss_feeds
from web_scraper import get_website_text_content
from summarizer import summarize_text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set page title and layout
st.set_page_config(page_title="RSS Feed Summary Generator", layout="wide")

# Initialize session state
if 'feeds' not in st.session_state:
    st.session_state.feeds = pd.DataFrame(columns=['url'])

# Title
st.title("RSS Feed Summary Generator")

# Input for new RSS feed URL
new_feed = st.text_input("Enter a new RSS feed URL:")
if st.button("Add Feed"):
    if new_feed:
        if new_feed not in st.session_state.feeds['url'].values:
            st.session_state.feeds = pd.concat([st.session_state.feeds, pd.DataFrame({'url': [new_feed]})], ignore_index=True)
            st.success(f"Added feed: {new_feed}")
        else:
            st.warning("This feed URL already exists.")
    else:
        st.warning("Please enter a valid URL.")

# Display and manage existing feeds
st.subheader("Existing Feeds")
for index, row in st.session_state.feeds.iterrows():
    col1, col2 = st.columns([3, 1])
    with col1:
        st.text(row['url'])
    with col2:
        if st.button("Remove", key=f"remove_{index}"):
            st.session_state.feeds = st.session_state.feeds.drop(index)
            st.experimental_rerun()

# Fetch and summarize feeds
if st.button("Fetch and Summarize Feeds"):
    if not st.session_state.feeds.empty:
        for _, row in st.session_state.feeds.iterrows():
            st.subheader(f"Feed: {row['url']}")
            feed_items = fetch_rss_feeds(row['url'])
            
            for item in feed_items[:10]:  # Process first 10 items
                st.write(f"**{item['title']}**")
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
                
                st.markdown("---")
    else:
        st.warning("No feeds available. Please add some RSS feed URLs.")

# Add some spacing at the bottom
st.markdown("<br><br>", unsafe_allow_html=True)
