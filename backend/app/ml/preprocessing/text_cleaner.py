# backend/app/ml/preprocessing/text_cleaner.py
import re
from typing import Dict
import logging

logger = logging.getLogger(__name__)

class TextPreprocessor:
    """Text preprocessing and feature extraction for ML analysis"""
    
    def __init__(self):
        pass
    
    def extract_features(self, text: str) -> Dict:
        """Extract text features for analysis"""
        if not text:
            return self._empty_features()
        
        # Basic text metrics
        words = text.split()
        word_count = len(words)
        char_count = len(text)
        
        # Caps analysis
        caps_count = sum(1 for c in text if c.isupper())
        caps_ratio = caps_count / char_count if char_count > 0 else 0
        
        # Punctuation analysis
        exclamation_count = text.count('!')
        question_count = text.count('?')
        has_exclamation = exclamation_count > 0
        has_question = question_count > 0
        
        # Emoji detection (basic)
        emoji_pattern = r'[😀-🙏🌀-🗿💀-🧿]'
        has_emoji = bool(re.search(emoji_pattern, text))
        
        # Calculate simple polarity score (for compatibility)
        positive_words = {'good', 'great', 'excellent', 'amazing', 'love', 'perfect', 'awesome'}
        negative_words = {'bad', 'terrible', 'awful', 'hate', 'horrible', 'worst', 'disgusting'}
        
        words_lower = [word.lower() for word in words]
        positive_count = sum(1 for word in words_lower if word in positive_words)
        negative_count = sum(1 for word in words_lower if word in negative_words)
        
        # Simple polarity calculation
        if positive_count + negative_count > 0:
            polarity = (positive_count - negative_count) / (positive_count + negative_count)
        else:
            polarity = 0.0
        
        return {
            'word_count': word_count,
            'char_count': char_count,
            'caps_ratio': round(caps_ratio, 3),
            'caps_count': caps_count,
            'exclamation_count': exclamation_count,
            'question_count': question_count,
            'has_exclamation': has_exclamation,
            'has_question': has_question,
            'has_emoji': has_emoji,
            'has_caps': caps_ratio > 0.3,
            'polarity': round(polarity, 3),
            'positive_words': positive_count,
            'negative_words': negative_count
        }
    
    def _empty_features(self) -> Dict:
        """Return empty features for null/empty text"""
        return {
            'word_count': 0,
            'char_count': 0,
            'caps_ratio': 0.0,
            'caps_count': 0,
            'exclamation_count': 0,
            'question_count': 0,
            'has_exclamation': False,
            'has_question': False,
            'has_emoji': False,
            'has_caps': False,
            'polarity': 0.0,
            'positive_words': 0,
            'negative_words': 0
        }
