# =============================================
# summarizer.py
# Core summarization logic
# Extractive  → scikit-learn + numpy
# Abstractive → transformers (BART)
# =============================================

import re
import numpy as np

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise         import cosine_similarity
from transformers                     import pipeline


# =============================================
# LENGTH SETTINGS MAP
# REDUCED significantly for shorter summaries
# =============================================
LENGTH_SETTINGS = {
    #         sentences    min_tokens  max_tokens
    'short':  (1,          10,         30),
    'medium': (2,          30,         60),
    'long':   (3,          60,         100),
}


# =============================================
# MAIN SUMMARIZER - routes to correct method
# =============================================
def summarize(text: str, method: str = 'extractive', length: str = 'medium') -> dict:
    """
    Main summarization function.

    Args:
        text   (str): Input text to summarize
        method (str): 'extractive' or 'abstractive'
        length (str): 'short', 'medium', or 'long'

    Returns:
        dict: {
            summary            : str,
            original_word_count: int,
            summary_word_count : int,
            method             : str,
            length             : str
        }
    """

    # Validate inputs
    text   = text.strip()
    method = method.lower()
    length = length.lower()

    if not text:
        raise ValueError("Input text cannot be empty.")

    if method not in ['extractive', 'abstractive']:
        raise ValueError("Method must be 'extractive' or 'abstractive'.")

    if length not in LENGTH_SETTINGS:
        raise ValueError("Length must be 'short', 'medium', or 'long'.")

    # Count original words
    original_word_count = len(text.split())

    # Minimum word requirement
    if original_word_count < 30:
        raise ValueError("Text must have at least 30 words for summarization.")

    # Route to correct method
    if method == 'extractive':
        summary = extractive_summarize(text, length)
    else:
        summary = abstractive_summarize(text, length)

    # Count summary words
    summary_word_count = len(summary.split())

    return {
        "summary"            : summary,
        "original_word_count": original_word_count,
        "summary_word_count" : summary_word_count,
        "method"             : method,
        "length"             : length
    }


# =============================================
# EXTRACTIVE SUMMARIZER
# Uses TF-IDF + cosine similarity to score
# and rank sentences, then picks top N
# =============================================
def extractive_summarize(text: str, length: str = 'medium') -> str:
    """
    Extractive summarization using TF-IDF scoring.

    Steps:
        1. Split text into sentences
        2. Compute TF-IDF matrix
        3. Score sentences by similarity to full text
        4. Pick top N sentences in original order

    Args:
        text   (str): Input text
        length (str): 'short', 'medium', or 'long'

    Returns:
        str: Extracted summary
    """

    # Get number of sentences for this length
    num_sentences = LENGTH_SETTINGS[length][0]

    # ---- Step 1: Split into sentences ----
    sentences = split_into_sentences(text)

    # If text has fewer sentences than needed return all
    if len(sentences) <= num_sentences:
        return text

    # ---- Step 2: TF-IDF Vectorization ----
    try:
        vectorizer = TfidfVectorizer(
            stop_words = 'english',
            min_df     = 1,
            max_df     = 0.9
        )

        tfidf_matrix = vectorizer.fit_transform(sentences)

    except Exception as e:
        raise RuntimeError(f"TF-IDF vectorization failed: {str(e)}")

    # ---- Step 3: Score sentences ----
    document_vector  = np.mean(tfidf_matrix.toarray(), axis=0).reshape(1, -1)
    sentence_vectors = tfidf_matrix.toarray()
    scores           = cosine_similarity(sentence_vectors, document_vector).flatten()

    # ---- Step 4: Pick top N sentences ----
    top_indices = np.argsort(scores)[::-1][:num_sentences]
    top_indices = sorted(top_indices)

    # Build summary
    summary = ' '.join([sentences[i] for i in top_indices])

    return summary


# =============================================
# ABSTRACTIVE SUMMARIZER
# Uses HuggingFace BART model
# =============================================

# Cache pipeline after first load
_abstractive_pipeline = None

def get_abstractive_pipeline():
    """
    Lazy load the BART summarization pipeline.
    Loads only once and caches for reuse.
    """
    global _abstractive_pipeline

    if _abstractive_pipeline is None:
        print("Loading BART model... (first time may take a moment)")
        _abstractive_pipeline = pipeline(
            "summarization",
            model  = "facebook/bart-large-cnn",
            device = -1                           # CPU
        )
        print("BART model loaded!")

    return _abstractive_pipeline


def abstractive_summarize(text: str, length: str = 'medium') -> str:
    """
    Abstractive summarization using BART model.

    Args:
        text   (str): Input text
        length (str): 'short', 'medium', or 'long'

    Returns:
        str: AI-generated summary
    """

    # Get token limits for this length
    _, min_tokens, max_tokens = LENGTH_SETTINGS[length]

    # Truncate input if too long
    max_input_chars = 1500
    if len(text) > max_input_chars:
        text = text[:max_input_chars]

    try:
        summarizer = get_abstractive_pipeline()

        result = summarizer(
            text,
            max_length = max_tokens,
            min_length = min_tokens,
            do_sample  = False,
            truncation = True
        )

        summary = result[0]['summary_text']

    except Exception as e:
        raise RuntimeError(f"Abstractive summarization failed: {str(e)}")

    return summary


# =============================================
# SENTENCE SPLITTER
# =============================================
def split_into_sentences(text: str) -> list:
    """
    Split text into individual sentences.

    Args:
        text (str): Input text

    Returns:
        list: List of sentence strings
    """
    sentence_endings = re.compile(r'(?<=[.!?])\s+')
    sentences        = sentence_endings.split(text)
    sentences        = [s.strip() for s in sentences if len(s.strip()) > 10]
    return sentences


# =============================================
# WORD COUNT UTILITY
# =============================================
def count_words(text: str) -> int:
    """
    Count number of words in text.

    Args:
        text (str): Input text

    Returns:
        int: Word count
    """
    return len(text.split()) if text.strip() else 0