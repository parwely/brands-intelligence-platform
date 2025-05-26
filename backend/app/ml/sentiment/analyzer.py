# backend/app/ml/sentiment/analyzer.py
from typing import Dict, List, Tuple
from textblob import TextBlob
import logging
import numpy as np
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
            'scam', 'fraud', 'lawsuit', 'sue', 'legal', 'court', 'lawyer', 'attorney',
            'boycott', 'protest', 'scandal', 'investigation', 'exposed', 'leaked',
            'urgent', 'emergency', 'critical', 'dangerous', 'unsafe', 'toxic',
            'recall', 'warning', 'alert', 'banned', 'illegal', 'violation'
        }
    
    def analyze_textblob(self, text: str) -> Dict:
        """TextBlob-based sentiment analysis"""
        try:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity  # -1 to 1
            subjectivity = blob.sentiment.subjectivity  # 0 to 1
            
            # Convert polarity to 0-1 scale
            sentiment_score = (polarity + 1) / 2
            
            # Classify sentiment with nuanced thresholds
            if polarity > 0.2:
                label = "positive"
            elif polarity < -0.2:
                label = "negative"
            else:
                label = "neutral"
            
            return {
                'sentiment_score': round(sentiment_score, 3),
                'sentiment_label': label,
                'confidence': round(abs(polarity), 3),
                'subjectivity': round(subjectivity, 3),
                'polarity': round(polarity, 3),
                'model': 'textblob'
            }
        except Exception as e:
            logger.error(f"TextBlob analysis failed: {e}")
            return self._default_sentiment()
    
    def analyze_keyword_based(self, text: str) -> Dict:
        """Enhanced keyword-based sentiment analysis"""
        text_lower = text.lower()
        words = set(text_lower.split())
        
        # Count keyword matches
        positive_matches = len(words.intersection(self.positive_words))
        negative_matches = len(words.intersection(self.negative_words))
        crisis_matches = len(words.intersection(self.crisis_keywords))
        
        # Calculate base sentiment score
        total_matches = positive_matches + negative_matches
        if total_matches == 0:
            base_score = 0.5  # Neutral
        else:
            base_score = positive_matches / total_matches
        
        # Adjust for text features
        features = self.preprocessor.extract_features(text)
        
        # Boost negative sentiment for caps, exclamations
        if features['caps_ratio'] > 0.3:
            base_score -= 0.1
        if features['exclamation_count'] > 2:
            base_score -= 0.05
        
        # Crisis keywords heavily impact sentiment
        if crisis_matches > 0:
            base_score = min(base_score, 0.2)
        
        # Clamp score between 0 and 1
        sentiment_score = max(0.0, min(1.0, base_score))
        
        # Determine label
        if sentiment_score > 0.6:
            label = "positive"
        elif sentiment_score < 0.4:
            label = "negative"
        else:
            label = "neutral"
        
        # Calculate confidence based on keyword strength
        confidence = min(0.9, (total_matches + crisis_matches) * 0.2)
        
        return {
            'sentiment_score': round(sentiment_score, 3),
            'sentiment_label': label,
            'confidence': round(confidence, 3),
            'positive_keywords': positive_matches,
            'negative_keywords': negative_matches,
            'crisis_keywords': crisis_matches,
            'model': 'keyword_based'
        }
    
    def analyze_hybrid(self, text: str) -> Dict:
        """Combine TextBlob and keyword-based analysis"""
        textblob_result = self.analyze_textblob(text)
        keyword_result = self.analyze_keyword_based(text)
        
        # Weighted combination (TextBlob 60%, Keywords 40%)
        tb_weight = 0.6
        kw_weight = 0.4
        
        combined_score = (
            textblob_result['sentiment_score'] * tb_weight +
            keyword_result['sentiment_score'] * kw_weight
        )
        
        # Use higher confidence model for final label
        if textblob_result['confidence'] > keyword_result['confidence']:
            final_label = textblob_result['sentiment_label']
            final_confidence = textblob_result['confidence']
        else:
            final_label = keyword_result['sentiment_label']
            final_confidence = keyword_result['confidence']
        
        # Override if crisis keywords detected
        if keyword_result['crisis_keywords'] > 0:
            final_label = "negative"
            final_confidence = max(final_confidence, 0.8)
            combined_score = min(combined_score, 0.3)
        
        return {
            'sentiment_score': round(combined_score, 3),
            'sentiment_label': final_label,
            'confidence': round(final_confidence, 3),
            'textblob_score': textblob_result['sentiment_score'],
            'keyword_score': keyword_result['sentiment_score'],
            'crisis_indicators': keyword_result['crisis_keywords'],
            'model': 'hybrid'
        }
    
    def batch_analyze(self, texts: List[str]) -> List[Dict]:
        """Analyze multiple texts efficiently"""
        results = []
        for text in texts:
            result = self.analyze_hybrid(text)
            results.append(result)
        return results
    
    def _default_sentiment(self) -> Dict:
        """Default sentiment when analysis fails"""
        return {
            'sentiment_score': 0.5,
            'sentiment_label': 'neutral',
            'confidence': 0.0,
            'model': 'default'
        }

# Test the analyzer
if __name__ == "__main__":
    analyzer = SentimentAnalyzer()
    
    test_texts = [
        "I absolutely love this brand! Amazing service and fantastic products! 😍",
        "This is a complete SCAM! Terrible company, worst experience ever! AVOID!",
        "The product is okay. Nothing special, but it works fine.",
        "URGENT WARNING: This company is fraudulent! Legal action needed!",
        "Great quality, fast shipping, reasonable price. Highly recommend! 👍"
    ]
    
    print("🧠 Testing Sentiment Analyzer...")
    print("=" * 60)
    
    for i, text in enumerate(test_texts, 1):
        print(f"\n{i}. Text: {text}")
        result = analyzer.analyze_hybrid(text)
        print(f"   Sentiment: {result['sentiment_label']} ({result['sentiment_score']:.3f})")
        print(f"   Confidence: {result['confidence']:.3f}")
        print(f"   TextBlob: {result['textblob_score']:.3f}, Keywords: {result['keyword_score']:.3f}")
        if result['crisis_indicators'] > 0:
            print(f"   🚨 CRISIS INDICATORS: {result['crisis_indicators']}")