# backend/app/ml/sentiment/analyzer.py
from typing import Dict, List
from textblob import TextBlob
import logging
import re
from ..preprocessing.text_cleaner import TextPreprocessor

logger = logging.getLogger(__name__)

class SentimentAnalyzer:
    """Multi-model sentiment analysis system"""
    
    def __init__(self):
        self.preprocessor = TextPreprocessor()
        self.positive_words = self._load_positive_words()
        self.negative_words = self._load_negative_words()
        self.crisis_keywords = self._load_crisis_keywords()
        
    def _load_positive_words(self) -> set:
        """Load positive sentiment keywords"""
        return {
            'amazing', 'awesome', 'excellent', 'fantastic', 'great', 'love', 'perfect',
            'wonderful', 'outstanding', 'brilliant', 'superb', 'incredible', 'marvelous',
            'exceptional', 'remarkable', 'impressive', 'delighted', 'satisfied', 'happy',
            'pleased', 'recommend', 'best', 'good', 'nice', 'beautiful', 'gorgeous',
            'revolutionary', 'cutting-edge', 'innovative', 'breakthrough'
        }
    
    def _load_negative_words(self) -> set:
        """Load negative sentiment keywords"""
        return {
            'terrible', 'awful', 'horrible', 'hate', 'worst', 'disgusting', 'pathetic',
            'useless', 'disappointing', 'annoying', 'frustrating', 'bad', 'poor', 'sad',
            'angry', 'furious', 'outraged', 'disgusted', 'appalled', 'devastated',
            'broken', 'failed', 'garbage', 'trash', 'nightmare', 'disaster', 'unacceptable'
        }
    
    def _load_crisis_keywords(self) -> set:
        """Load crisis-indicating keywords"""
        return {
            'scam', 'fraud', 'lawsuit', 'sue', 'legal', 'court', 'lawyer', 'attorney',
            'boycott', 'protest', 'scandal', 'investigation', 'exposed', 'leaked',
            'urgent', 'emergency', 'critical', 'dangerous', 'unsafe', 'toxic',
            'recall', 'warning', 'alert', 'banned', 'illegal', 'violation', 'false claims'
        }
    
    def analyze_hybrid(self, text: str) -> Dict:
        """Main analysis method combining multiple approaches"""
        try:
            # TextBlob analysis
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            sentiment_score = (polarity + 1) / 2  # Convert to 0-1 scale
            
            # Keyword analysis
            text_lower = text.lower()
            words = set(re.findall(r'\b\w+\b', text_lower))
            
            positive_matches = len(words.intersection(self.positive_words))
            negative_matches = len(words.intersection(self.negative_words))
            crisis_matches = len(words.intersection(self.crisis_keywords))
            
            # Adjust sentiment based on keywords
            if positive_matches > negative_matches:
                sentiment_score = max(sentiment_score, 0.6 + positive_matches * 0.1)
            elif negative_matches > positive_matches:
                sentiment_score = min(sentiment_score, 0.4 - negative_matches * 0.1)
            
            # Crisis keywords override sentiment
            if crisis_matches > 0:
                sentiment_score = min(sentiment_score, 0.2)
            
            # Clamp score
            sentiment_score = max(0.0, min(1.0, sentiment_score))
            
            # Determine label
            if sentiment_score > 0.6:
                label = "positive"
            elif sentiment_score < 0.4:
                label = "negative"
            else:
                label = "neutral"
            
            # Calculate confidence
            confidence = abs(polarity) + (positive_matches + negative_matches + crisis_matches) * 0.1
            confidence = min(0.9, confidence)
            
            return {
                'sentiment_score': round(sentiment_score, 3),
                'sentiment_label': label,
                'confidence': round(confidence, 3),
                'textblob_score': round((polarity + 1) / 2, 3),
                'keyword_score': round(sentiment_score, 3),
                'crisis_indicators': crisis_matches,
                'model': 'hybrid'
            }
            
        except Exception as e:
            logger.error(f"Sentiment analysis failed: {e}")
            return {
                'sentiment_score': 0.5,
                'sentiment_label': 'neutral',
                'confidence': 0.0,
                'crisis_indicators': 0,
                'model': 'error'
            }