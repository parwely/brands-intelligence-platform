# backend/app/services/ml_service.py
from typing import Dict, List
import logging
import asyncio
from ..ml.sentiment.analyzer import SentimentAnalyzer
# from ..ml.preprocessing.text_cleaner import TextPreprocessor  # Temporarily disabled

logger = logging.getLogger(__name__)

class MLService:
    """Main ML service orchestrating all AI operations"""
    
    def __init__(self):
        try:
            self.sentiment_analyzer = SentimentAnalyzer()
            # self.preprocessor = TextPreprocessor()  # Temporarily disabled
            self._model_version = "1.0.0"
            logger.info("ML Service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize ML Service: {e}")
            raise
    
    def _extract_basic_features(self, text: str) -> Dict:
        """Basic feature extraction without external dependencies"""
        if not text:
            return {
                'word_count': 0, 'caps_ratio': 0.0, 'exclamation_count': 0,
                'question_count': 0, 'has_caps': False, 'has_exclamation': False,
                'has_question': False, 'has_emoji': False, 'polarity': 0.0
            }
        
        words = text.split()
        word_count = len(words)
        caps_count = sum(1 for c in text if c.isupper())
        caps_ratio = caps_count / len(text) if text else 0
        exclamation_count = text.count('!')
        question_count = text.count('?')
        
        return {
            'word_count': word_count,
            'caps_ratio': round(caps_ratio, 3),
            'exclamation_count': exclamation_count,
            'question_count': question_count,
            'has_caps': caps_ratio > 0.3,
            'has_exclamation': exclamation_count > 0,
            'has_question': question_count > 0,
            'has_emoji': False,  # Simplified
            'polarity': 0.0
        }
        
    async def analyze_mention_sentiment(self, text: str) -> Dict:
        """Comprehensive analysis of a single mention"""
        try:
            # Get text features
            features = self._extract_basic_features(text)
            
            # Analyze sentiment with hybrid approach
            sentiment = self.sentiment_analyzer.analyze_hybrid(text)
            
            # Calculate crisis probability
            crisis_prob = await self._calculate_crisis_probability(sentiment, features)
            
            # Calculate urgency score
            urgency = self._calculate_urgency_score(sentiment, features)
            
            return {
                'sentiment_score': sentiment['sentiment_score'],
                'sentiment_label': sentiment['sentiment_label'],
                'confidence': sentiment['confidence'],
                'crisis_probability': crisis_prob,
                'urgency_score': urgency,
                'crisis_indicators': sentiment.get('crisis_indicators', 0),
                'text_features': {
                    'word_count': features['word_count'],
                    'has_caps': features['has_caps'],
                    'has_exclamation': features['has_exclamation'],
                    'has_emoji': features['has_emoji'],
                    'caps_ratio': features['caps_ratio'],
                    'polarity': features['polarity']
                },
                'model_info': {
                    'model': sentiment['model'],
                    'version': self._model_version,
                    'textblob_score': sentiment.get('textblob_score'),
                    'keyword_score': sentiment.get('keyword_score')
                }
            }
        except Exception as e:
            logger.error(f"ML analysis failed for text '{text[:50]}...': {e}")
            return self._error_response()
    
    async def batch_analyze_mentions(self, texts: List[str]) -> List[Dict]:
        """Analyze multiple mentions efficiently"""
        try:
            tasks = [self.analyze_mention_sentiment(text) for text in texts]
            return await asyncio.gather(*tasks)
        except Exception as e:
            logger.error(f"Batch analysis failed: {e}")
            return [self._error_response() for _ in texts]
    
    async def _calculate_crisis_probability(self, sentiment: Dict, features: Dict) -> float:
        """Advanced crisis probability calculation"""
        crisis_score = 0.0
        
        # Base score from sentiment
        sentiment_score = sentiment['sentiment_score']
        if sentiment_score < 0.2:
            crisis_score += 0.5
        elif sentiment_score < 0.4:
            crisis_score += 0.3
        
        # Crisis keywords are strong indicators
        crisis_indicators = sentiment.get('crisis_indicators', 0)
        crisis_score += min(0.4, crisis_indicators * 0.2)
        
        # Text pattern indicators
        if features['caps_ratio'] > 0.5:  # Lots of caps = urgency
            crisis_score += 0.2
        if features['exclamation_count'] > 3:  # Multiple exclamations
            crisis_score += 0.15
        if features['has_emoji'] and sentiment_score < 0.3:  # Emotional negative content
            crisis_score += 0.1
        
        # High confidence negative sentiment
        if sentiment['confidence'] > 0.8 and sentiment['sentiment_label'] == 'negative':
            crisis_score += 0.2
        
        # Very short angry messages are often more urgent
        if features['word_count'] < 10 and sentiment_score < 0.3:
            crisis_score += 0.1
        
        return min(1.0, crisis_score)
    
    def _calculate_urgency_score(self, sentiment: Dict, features: Dict) -> float:
        """Calculate how urgent a response is needed"""
        urgency = 0.0
        
        # High crisis probability = high urgency
        crisis_indicators = sentiment.get('crisis_indicators', 0)
        urgency += crisis_indicators * 0.3
        
        # Multiple exclamations suggest urgency
        urgency += min(0.3, features['exclamation_count'] * 0.1)
        
        # All caps text suggests urgency
        if features['caps_ratio'] > 0.7:
            urgency += 0.4
        
        # Questions might need responses
        if features['has_question']:
            urgency += 0.2
        
        # Recent and negative = urgent
        if sentiment['sentiment_score'] < 0.3:
            urgency += 0.3
        
        return min(1.0, urgency)
    
    def _error_response(self) -> Dict:
        """Default response when analysis fails"""
        return {
            'sentiment_score': 0.5,
            'sentiment_label': 'neutral',
            'confidence': 0.0,
            'crisis_probability': 0.0,
            'urgency_score': 0.0,
            'crisis_indicators': 0,
            'text_features': {},
            'model_info': {'model': 'error', 'version': self._model_version}
        }
    
    async def get_model_info(self) -> Dict:
        """Get information about loaded models"""
        return {
            'version': self._model_version,
            'models': {
                'sentiment': 'Hybrid (TextBlob + Keywords)',
                'preprocessing': 'NLTK + Custom Rules',
                'crisis_detection': 'Rule-based Algorithm'
            },
            'capabilities': [
                'Sentiment Analysis',
                'Crisis Detection',
                'Urgency Scoring',
                'Text Feature Extraction'
            ],
            'languages': ['English'],
            'status': 'active'
        }

# Global ML service instance
ml_service = MLService()