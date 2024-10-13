import nltk
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.probability import FreqDist
from heapq import nlargest
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Download necessary NLTK data
logger.info("Downloading NLTK data...")
for resource in ['punkt', 'stopwords', 'averaged_perceptron_tagger', 'punkt_tab']:
    try:
        nltk.download(resource, quiet=True)
        logger.info(f"Successfully downloaded {resource}")
    except Exception as e:
        logger.error(f"Failed to download {resource}: {str(e)}")

def summarize_text(text, num_sentences=3):
    try:
        # Tokenize the text into sentences and words
        sentences = sent_tokenize(text)
        words = word_tokenize(text.lower())

        # Remove stopwords
        stop_words = set(stopwords.words('english'))
        words = [word for word in words if word not in stop_words]

        # Calculate word frequencies
        freq = FreqDist(words)

        # Score sentences based on word frequencies
        sentence_scores = {}
        for i, sentence in enumerate(sentences):
            for word in word_tokenize(sentence.lower()):
                if word in freq:
                    if i not in sentence_scores:
                        sentence_scores[i] = freq[word]
                    else:
                        sentence_scores[i] += freq[word]

        # Get the top N sentences with highest scores
        summary_sentences = nlargest(min(num_sentences, len(sentences)), sentence_scores, key=sentence_scores.get)
        summary = ' '.join([sentences[i] for i in sorted(summary_sentences)])

        return summary
    except LookupError as e:
        logger.error(f"NLTK LookupError: {str(e)}")
        return f"Error: Unable to summarize due to missing NLTK data. Details: {str(e)}"
    except Exception as e:
        logger.error(f"Summarization Error: {str(e)}")
        return f"Error: Unable to generate summary. Details: {str(e)}"
