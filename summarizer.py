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

def postprocess_summary(summary):
    # Join sentences
    summary = ' '.join(summary)
    # Capitalize first letter
    summary = summary[0].upper() + summary[1:]
    # Ensure the summary ends with a period
    if not summary.endswith('.'):
        summary += '.'
    return summary

def summarize_with_chatgpt(text, max_tokens=150):
    try:
        response = openai.Completion.create(
            engine="text-davinci-002",
            prompt=f"Please summarize the following text:\n\n{text}\n\nSummary:",
            max_tokens=max_tokens,
            n=1,
            stop=None,
            temperature=0.7,
        )
        return response.choices[0].text.strip()
    except Exception as e:
        logger.error(f"Error using ChatGPT API: {str(e)}")
        return None

def summarize_text(text, num_sentences=3, max_words=150):
    try:
        preprocessed_text = preprocess_text(text)
        
        # Try to use ChatGPT for summarization
        chatgpt_summary = summarize_with_chatgpt(preprocessed_text, max_tokens=max_words)
        if chatgpt_summary:
            return chatgpt_summary

        # If ChatGPT fails, use the existing summarization method
        sentences = sent_tokenize(preprocessed_text)
        words = word_tokenize(preprocessed_text.lower())

        # Remove stopwords (English and Turkish)
        stop_words = set(stopwords.words('english') + stopwords.words('turkish'))
        words = [word for word in words if word not in stop_words]

        # Calculate word frequencies
        freq = FreqDist(words)

        # Score sentences based on word frequencies, position, and length
        sentence_scores = {}
        for i, sentence in enumerate(sentences):
            sentence_words = word_tokenize(sentence.lower())
            sentence_score = sum(freq[word] for word in sentence_words if word in freq)
            
            # Consider sentence position
            if i < len(sentences) * 0.2 or i > len(sentences) * 0.8:
                sentence_score *= 1.5
            
            # Consider sentence length
            if 5 <= len(sentence_words) <= 25:
                sentence_score *= 1.2
            
            # Look for key phrases (English and Turkish)
            key_phrases = ["in conclusion", "to summarize", "in summary", "finally", "lastly",
                           "sonuç olarak", "özetlemek gerekirse", "özetle", "son olarak"]
            if any(phrase in sentence.lower() for phrase in key_phrases):
                sentence_score *= 1.5
            
            sentence_scores[i] = sentence_score

        # Get the top N sentences with highest scores
        summary_sentences = nlargest(min(num_sentences, len(sentences)), sentence_scores, key=sentence_scores.get)
        summary = [sentences[i] for i in sorted(summary_sentences)]

        # Post-process the summary
        final_summary = postprocess_summary(summary)

        # Truncate the summary to max_words
        words = final_summary.split()
        if len(words) > max_words:
            final_summary = ' '.join(words[:max_words]) + '...'

        return final_summary
    except LookupError as e:
        logger.error(f"NLTK LookupError: {str(e)}")
        return f"Error: Unable to summarize due to missing NLTK data. Details: {str(e)}"
    except Exception as e:
        logger.error(f"Summarization Error: {str(e)}")
        return f"Error: Unable to generate summary. Details: {str(e)}"
