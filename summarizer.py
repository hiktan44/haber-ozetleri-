import nltk
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.probability import FreqDist
from heapq import nlargest
import logging
import re
import unicodedata
import os
from openai import OpenAI

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Download necessary NLTK data
logger.info("Downloading NLTK data...")
for resource in ['punkt', 'stopwords']:
    try:
        nltk.download(resource, quiet=True)
        logger.info(f"Successfully downloaded {resource}")
    except Exception as e:
        logger.error(f"Failed to download {resource}: {str(e)}")

# Set up OpenAI API key
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Custom Turkish stop words (extend this list as needed)
turkish_stop_words = set([
    've', 'veya', 'bir', 'bu', 'şu', 'o', 'de', 'da', 'ki', 'ile', 'için',
    'ama', 'fakat', 'ancak', 'lakin', 'çünkü', 'zira', 'dolayı', 'nedeniyle',
    'gibi', 'kadar', 'olarak', 'üzere', 'diye', 'mi', 'mı', 'mu', 'mü'
])

def preprocess_text(text):
    logger.debug("Preprocessing text...")
    # Normalize Unicode characters
    text = unicodedata.normalize('NFKC', text)
    # Remove unnecessary whitespace
    text = ' '.join(text.split())
    # Keep Turkish-specific characters
    text = re.sub(r'[^\w\s\u00c7\u00e7\u011e\u011f\u0130\u0131\u00d6\u00f6\u015e\u015f\u00dc\u00fc]', '', text)
    logger.debug("Text preprocessing completed")
    return text

def summarize_with_chatgpt(text, num_sentences, max_words):
    logger.info("Attempting to summarize with ChatGPT...")
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"Sen bir özetleme asistanısın. Aşağıdaki metni Türkçe olarak {num_sentences} cümle ile özetle, {max_words} kelimeyi geçmeyecek şekilde. Özetin tutarlı olmasını ve cümlelerin yarıda kesilmemesini sağla."},
                {"role": "user", "content": text}
            ],
            max_tokens=max_words * 2,  # Allowing some buffer for the model
            n=1,
            temperature=0.7,
        )
        summary = response.choices[0].message.content.strip()
        
        # Ensure we don't exceed the max_words limit
        words = summary.split()
        if len(words) > max_words:
            summary = ' '.join(words[:max_words])
            # Ensure we don't cut off mid-sentence
            if not summary.endswith('.'):
                summary = ' '.join(summary.split('.')[:-1]) + '.'
        
        logger.info("Successfully generated summary with ChatGPT")
        return summary
    except Exception as e:
        logger.error(f"Error using ChatGPT API: {str(e)}")
        return None

def fallback_summarize(text, num_sentences, max_words):
    logger.info("Using fallback summarization method...")
    try:
        sentences = sent_tokenize(text)
        words = word_tokenize(text.lower())

        # Remove stopwords (Turkish)
        stop_words = set(stopwords.words('turkish')).union(turkish_stop_words)
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

        logger.info("Fallback summarization completed successfully")
        return final_summary
    except Exception as e:
        logger.error(f"Fallback summarization error: {str(e)}")
        return f"Hata: Özet oluşturulamadı. Detaylar: {str(e)}"

def summarize_text(text, num_sentences=3, max_words=150):
    logger.info(f"Summarizing text with {num_sentences} sentences and max {max_words} words...")
    try:
        preprocessed_text = preprocess_text(text)
        
        # Try to use ChatGPT for summarization
        chatgpt_summary = summarize_with_chatgpt(preprocessed_text, num_sentences, max_words)
        if chatgpt_summary:
            logger.info("Successfully summarized using ChatGPT")
            return chatgpt_summary

        # If ChatGPT fails, use the fallback summarization method
        logger.info("ChatGPT summarization failed. Using fallback method.")
        return fallback_summarize(preprocessed_text, num_sentences, max_words)

    except Exception as e:
        logger.error(f"Summarization Error: {str(e)}")
        return f"Hata: Özet oluşturulamadı. Detaylar: {str(e)}"
