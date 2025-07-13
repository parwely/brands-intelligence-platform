# backend/app/ml/sentiment/analyzer.py
from typing import Dict
import logging
import re

logger = logging.getLogger(__name__)

class SentimentAnalyzer:
    """Keyword-based sentiment analysis system"""
    
    def __init__(self):
        self.positive_words = self._load_positive_words()
        self.negative_words = self._load_negative_words()
        self.crisis_keywords = self._load_crisis_keywords()
        
    def _load_positive_words(self) -> set:
        """Load positive sentiment keywords"""
        return {
            'amazing', 'awesome', 'excellent', 'fantastic', 'great', 'love', 'perfect',
            'wonderful', 'outstanding', 'brilliant', 'superb', 'incredible', 'marvelous',
            'exceptional', 'remarkable', 'impressive', 'delighted', 'satisfied', 'happy',
            'pleased', 'recommend', 'best', 'good', 'nice', 'beautiful', 'gorgeous'
        }
    
    def _load_negative_words(self) -> set:
        """Load negative sentiment keywords"""
        return {
            'terrible', 'awful', 'horrible', 'hate', 'worst', 'disgusting', 'pathetic',
            'useless', 'disappointing', 'annoying', 'frustrating', 'bad', 'poor', 'sad',
            'angry', 'furious', 'outraged', 'disgusted', 'appalled', 'devastated',
            'broken', 'failed', 'garbage', 'trash', 'nightmare', 'disaster'
        }
    
    def _load_crisis_keywords(self) -> set:
        """Load crisis-indicating keywords"""
        return {
            'scam', 'fraud', 'lawsuit', 'sue', 'legal', 'court', 'boycott', 'protest',
            'scandal', 'investigation', 'urgent', 'emergency', 'critical', 'dangerous',
            'recall', 'warning', 'alert', 'banned', 'illegal'
        }
    
    def analyze_hybrid(self, text: str) -> Dict:
        """Keyword-based sentiment analysis"""
        try:
            text_lower = text.lower()
            words = set(re.findall(r'\b\w+\b', text_lower))
            
            positive_matches = len(words.intersection(self.positive_words))
            negative_matches = len(words.intersection(self.negative_words))
            crisis_matches = len(words.intersection(self.crisis_keywords))
            
            # Calculate sentiment score
            total_matches = positive_matches + negative_matches
            if total_matches > 0:
                polarity = (positive_matches - negative_matches) / total_matches
                sentiment_score = (polarity + 1) / 2
            else:
                polarity = 0.0
                sentiment_score = 0.5
            
            # Apply keyword boosts
            if positive_matches > negative_matches:
                sentiment_score = max(sentiment_score, 0.6)
            elif negative_matches > positive_matches:
                sentiment_score = min(sentiment_score, 0.4)
            
            # Crisis keywords override sentiment
            if crisis_matches > 0:
                sentiment_score = min(sentiment_score, 0.2)
            
            # Determine label
            if sentiment_score > 0.6:
                label = "positive"
            elif sentiment_score < 0.4:
                label = "negative"
            else:
                label = "neutral"
            
            # Calculate confidence
            confidence = min(0.9, (total_matches + crisis_matches) * 0.2)
            
            return {
                'sentiment_score': round(sentiment_score, 3),
                'sentiment_label': label,
                'confidence': round(confidence, 3),
                'crisis_indicators': crisis_matches,
                'model': 'keyword_based'
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