import nltk
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.probability import FreqDist
from heapq import nlargest
import logging
import re
import unicodedata
import os
import openai

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Download necessary NLTK data
logger.info("Downloading NLTK data...")
for resource in ['punkt', 'stopwords', 'averaged_perceptron_tagger']:
    try:
        nltk.download(resource, quiet=True)
        logger.info(f"Successfully downloaded {resource}")
    except Exception as e:
        logger.error(f"Failed to download {resource}: {str(e)}")

# Set up OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

def preprocess_text(text):
    # Normalize Unicode characters
    text = unicodedata.normalize('NFKC', text)
    # Remove unnecessary whitespace
    text = ' '.join(text.split())
    # Remove special characters but keep Turkish-specific characters
    text = re.sub(r'[^\w\s\u00c7\u00e7\u011e\u011f\u0130\u0131\u00d6\u00f6\u015e\u015f\u00dc\u00fc]', '', text)
    return text

def summarize_with_chatgpt(text, num_sentences, max_words):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"You are a summarization assistant. Summarize the following text in {num_sentences} sentences, not exceeding {max_words} words. Ensure the summary is coherent and doesn't cut off mid-sentence."},
                {"role": "user", "content": text}
            ],
            max_tokens=max_words * 2,  # Allowing some buffer for the model
            n=1,
            stop=None,
            temperature=0.7,
        )
        summary = response.choices[0].message['content'].strip()
        
        # Ensure we don't exceed the max_words limit
        words = summary.split()
        if len(words) > max_words:
            summary = ' '.join(words[:max_words])
            # Ensure we don't cut off mid-sentence
            if not summary.endswith('.'):
                summary = ' '.join(summary.split('.')[:-1]) + '.'
        
        return summary
    except Exception as e:
        logger.error(f"Error using ChatGPT API: {str(e)}")
        return None

def fallback_summarize(text, num_sentences, max_words):
    try:
        sentences = sent_tokenize(text)
        words = word_tokenize(text.lower())

        # Remove stopwords (English and Turkish)
        stop_words = set(stopwords.words('english') + stopwords.words('turkish'))
        words = [word for word in words if word not in stop_words]

        # Calculate word frequencies
        freq = FreqDist(words)

        # Score sentences based on word frequencies
        sentence_scores = {}
        for i, sentence in enumerate(sentences):
            sentence_words = word_tokenize(sentence.lower())
            sentence_score = sum(freq[word] for word in sentence_words if word in freq)
            sentence_scores[i] = sentence_score

        # Get the top N sentences with highest scores
        summary_sentences = nlargest(min(num_sentences, len(sentences)), sentence_scores, key=sentence_scores.get)
        summary = [sentences[i] for i in sorted(summary_sentences)]

        # Join sentences and truncate to max_words
        final_summary = ' '.join(summary)
        words = final_summary.split()
        if len(words) > max_words:
            final_summary = ' '.join(words[:max_words])
            # Ensure we don't cut off mid-sentence
            if not final_summary.endswith('.'):
                final_summary = ' '.join(final_summary.split('.')[:-1]) + '.'

        return final_summary
    except Exception as e:
        logger.error(f"Fallback summarization error: {str(e)}")
        return f"Error: Unable to generate summary. Details: {str(e)}"

def summarize_text(text, num_sentences=3, max_words=150):
    try:
        preprocessed_text = preprocess_text(text)
        
        # Try to use ChatGPT for summarization
        chatgpt_summary = summarize_with_chatgpt(preprocessed_text, num_sentences, max_words)
        if chatgpt_summary:
            return chatgpt_summary

        # If ChatGPT fails, use the fallback summarization method
        logger.info("ChatGPT summarization failed. Using fallback method.")
        return fallback_summarize(preprocessed_text, num_sentences, max_words)

    except Exception as e:
        logger.error(f"Summarization Error: {str(e)}")
        return f"Error: Unable to generate summary. Details: {str(e)}"
