# backend/app/ml/preprocessing/text_cleaner.py
import re
import string
from typing import Dict
import logging

logger = logging.getLogger(__name__)

# Simple NLTK alternative for basic tokenization
def simple_tokenize(text: str) -> list:
    """Basic tokenization without NLTK dependency"""
    # Remove punctuation and split on whitespace
    text = re.sub(r'[^\w\s]', ' ', text)
    return [word.lower() for word in text.split() if len(word) > 2]

class TextPreprocessor:
    """Text preprocessing for sentiment analysis"""
    
    def __init__(self):
        # Basic stopwords (subset of NLTK stopwords)
        self.stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
            'by', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they',
            'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does',
            'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can'
        }
    
    def clean_text(self, text: str) -> str:
        """Basic text cleaning"""
        if not text or not isinstance(text, str):
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove URLs
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        
        # Remove user mentions and hashtags (but keep content)
        text = re.sub(r'@\w+', '', text)
        text = re.sub(r'#(\w+)', r'\1', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def extract_features(self, text: str) -> Dict:
        """Extract text features for analysis"""
        if not text:
            return self._empty_features()
        
        try:
            cleaned = self.clean_text(text)
            words = text.split()
            
            # Basic features
            word_count = len(words)
            char_count = len(text)
            
            # Pattern features
            has_exclamation = '!' in text
            has_question = '?' in text
            has_caps = any(c.isupper() for c in text)
            caps_ratio = sum(1 for c in text if c.isupper()) / len(text) if text else 0
            
            # Count features
            exclamation_count = text.count('!')
            question_count = text.count('?')
            
            # Emoji detection (basic)
            has_emoji = bool(re.search(r'[😀-🙏🌀-🗿🚀-🛿☀-⛿]', text))
            
            return {
                'word_count': word_count,
                'char_count': char_count,
                'sentence_count': text.count('.') + text.count('!') + text.count('?') + 1,
                'polarity': 0.0,  # Will be filled by sentiment analyzer
                'subjectivity': 0.0,  # Will be filled by sentiment analyzer
                'has_exclamation': has_exclamation,
                'has_question': has_question,
                'has_caps': has_caps,
                'caps_ratio': round(caps_ratio, 3),
                'has_emoji': has_emoji,
                'exclamation_count': exclamation_count,
                'question_count': question_count,
                'cleaned_text': cleaned,
                'advanced_cleaned': cleaned,
                'avg_word_length': round(sum(len(word) for word in words) / word_count, 2) if word_count > 0 else 0
            }
        except Exception as e:
            logger.error(f"Feature extraction failed: {e}")
            return self._empty_features()
    
    def _empty_features(self) -> Dict:
        """Return empty features dict"""
        return {
            'word_count': 0, 'char_count': 0, 'sentence_count': 0,
            'polarity': 0.0, 'subjectivity': 0.0, 'has_exclamation': False,
            'has_question': False, 'has_caps': False, 'caps_ratio': 0.0,
            'has_emoji': False, 'exclamation_count': 0, 'question_count': 0,
            'cleaned_text': '', 'advanced_cleaned': '', 'avg_word_length': 0.0
        }