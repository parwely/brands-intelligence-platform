# backend/app/services/ml_service.py
# ml service orchestrating all AI operations
from typing import Dict, List
import logging
import asyncio
from ..ml.sentiment.analyzer import SentimentAnalyzer
from ..ml.preprocessing.text_cleaner import TextPreprocessor

logger = logging.getLogger(__name__)

class MLService:
    """Main ML service orchestrating all AI operations"""
    
    def __init__(self):
        self.sentiment_analyzer = SentimentAnalyzer()
        self.preprocessor = TextPreprocessor()
        self._model_version = "1.0.0"
        
    async def analyze_mention_sentiment(self, text: str) -> Dict:
        """Comprehensive analysis of a single mention"""
        try:
            # Get text features
            features = self.preprocessor.extract_features(text)
            
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
                    'caps_ratio': features['caps_ratio']
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
        tasks = [self.analyze_mention_sentiment(text) for text in texts]
        return await asyncio.gather(*tasks)
    
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

# Test the service
if __name__ == "__main__":
    import asyncio
    
    async def test_ml_service():
        service = MLService()
        
        test_cases = [
            "I absolutely love this brand! Best customer service ever! 🌟",
            "SCAM ALERT! This company is FRAUDULENT! Do NOT buy from them!!!",
            "The product is okay. Nothing special, but does the job.",
            "Urgent! My order is missing and customer support won't help!",
            "Great quality, fast shipping, reasonable price. Recommended."
        ]
        
        print("🧠 Testing Complete ML Service...")
        print("=" * 60)
        
        for i, text in enumerate(test_cases, 1):
            print(f"\n{i}. Text: {text}")
            result = await service.analyze_mention_sentiment(text)
            
            print(f"   Sentiment: {result['sentiment_label']} ({result['sentiment_score']:.3f})")
            print(f"   Confidence: {result['confidence']:.3f}")
            print(f"   Crisis Risk: {result['crisis_probability']:.3f}")
            print(f"   Urgency: {result['urgency_score']:.3f}")
            
            if result['crisis_probability'] > 0.5:
                print(f"   🚨 HIGH CRISIS RISK!")
            if result['urgency_score'] > 0.6:
                print(f"   ⚡ URGENT RESPONSE NEEDED!")
        
        # Test model info
        model_info = await service.get_model_info()
        print(f"\n📊 Model Info: {model_info}")
    
    asyncio.run(test_ml_service())