import PyPDF2
import pdfplumber
from textstat import flesch_reading_ease, flesch_kincaid_grade, automated_readability_index
import re
from typing import Dict, List, Tuple, Optional
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from collections import Counter
import io
import base64
import logging  # Add this line
logger = logging.getLogger(__name__)  # And this line

class EnhancedPDFProcessor:
    """Enhanced PDF processor with readability analysis"""

    def __init__(self):
        try:
            self.stop_words = set(stopwords.words('english'))
        except LookupError:
            # Fallback if NLTK data not available
            self.stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}

    def extract_text_from_bytes(self, pdf_bytes: bytes) -> str:
        """Extract text from PDF bytes"""
        text = ""
        try:
            # Try pdfplumber first
            with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            logger.warning(f"pdfplumber extraction failed: {e}, trying PyPDF2")
            # Fallback to PyPDF2
            try:
                reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
                for page in reader.pages:
                    text += page.extract_text() + "\n"
            except Exception as e2:
                logger.error(f"PyPDF2 extraction also failed: {e2}")
                text = "Error: Could not extract text from PDF"

        return text

    def extract_text_from_file(self, pdf_path: str) -> str:
        """Extract text from PDF file"""
        with open(pdf_path, 'rb') as file:
            return self.extract_text_from_bytes(file.read())

    def clean_text(self, text: str) -> str:
        """Clean and normalize extracted text"""
        if not text:
            return ""

        # Remove extra whitespace and normalize line breaks
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\n+', '\n', text)

        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s.,!?;:\-\'"()@]', '', text)

        # Fix common PDF extraction issues
        text = text.replace('- ', '')  # Remove hyphenation at line breaks
        text = re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', text)  # Add space between camelCase

        return text.strip()

    def analyze_readability(self, text: str) -> Dict[str, float]:
        """Analyze text readability metrics"""
        if not text or len(text.strip()) < 10:
            return {
                'error': 'Text too short for analysis',
                'word_count': 0,
                'sentence_count': 0
            }

        try:
            # Tokenize text
            sentences = sent_tokenize(text)
            words = word_tokenize(text)

            readability_scores = {
                'flesch_reading_ease': flesch_reading_ease(text),
                'flesch_kincaid_grade': flesch_kincaid_grade(text),
                'automated_readability_index': automated_readability_index(text),
                'word_count': len([w for w in words if w.isalpha()]),
                'sentence_count': len(sentences),
                'avg_sentence_length': len(words) / len(sentences) if sentences else 0,
                'avg_word_length': sum(len(w) for w in words if w.isalpha()) / len([w for w in words if w.isalpha()]) if words else 0
            }

            # Interpret Flesch Reading Ease score
            fre_score = readability_scores['flesch_reading_ease']
            if fre_score >= 90:
                readability_level = "Very Easy"
            elif fre_score >= 80:
                readability_level = "Easy"
            elif fre_score >= 70:
                readability_level = "Fairly Easy"
            elif fre_score >= 60:
                readability_level = "Standard"
            elif fre_score >= 50:
                readability_level = "Fairly Difficult"
            elif fre_score >= 30:
                readability_level = "Difficult"
            else:
                readability_level = "Very Difficult"

            readability_scores['readability_level'] = readability_level

        except Exception as e:
            logger.error(f"Error calculating readability: {e}")
            readability_scores = {
                "error": str(e),
                "word_count": len(text.split()) if text else 0,
                "sentence_count": len(text.split('.')) if text else 0
            }

        return readability_scores

    def extract_key_phrases(self, text: str, top_n: int = 15) -> List[str]:
        """Extract key phrases from text"""
        if not text:
            return []

        try:
            words = word_tokenize(text.lower())
            words = [word for word in words if word.isalpha() and len(word) > 2 and word not in self.stop_words]

            # Frequency-based key phrase extraction
            word_freq = Counter(words)
            return [word for word, freq in word_freq.most_common(top_n)]
        except Exception as e:
            logger.error(f"Error extracting key phrases: {e}")
            return []

    def process_pdf(self, pdf_path: str = None, pdf_bytes: bytes = None) -> Dict:
        """Complete PDF processing with readability analysis"""
        try:
            if pdf_path:
                logger.info(f"Processing PDF file: {pdf_path}")
                raw_text = self.extract_text_from_file(pdf_path)
            elif pdf_bytes:
                logger.info("Processing PDF from bytes")
                raw_text = self.extract_text_from_bytes(pdf_bytes)
            else:
                raise ValueError("Either pdf_path or pdf_bytes must be provided")

            if not raw_text or raw_text.startswith("Error:"):
                return {
                    'error': 'Failed to extract text from PDF',
                    'raw_text': raw_text or '',
                    'success': False
                }

            # Clean text
            cleaned_text = self.clean_text(raw_text)

            # Analyze readability
            readability_metrics = self.analyze_readability(cleaned_text)

            # Extract key phrases
            key_phrases = self.extract_key_phrases(cleaned_text)

            return {
                'raw_text': raw_text,
                'cleaned_text': cleaned_text,
                'readability_metrics': readability_metrics,
                'key_phrases': key_phrases,
                'text_length': len(cleaned_text),
                'word_count': readability_metrics.get('word_count', 0),
                'success': True
            }

        except Exception as e:
            logger.error(f"Error processing PDF: {e}")
            return {
                'error': str(e),
                'success': False,
                'raw_text': '',
                'cleaned_text': ''
            }
