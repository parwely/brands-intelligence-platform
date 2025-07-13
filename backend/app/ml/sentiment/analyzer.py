# backend/app/ml/sentiment/analyzer.py
from typing import Dict, List
import logging
import re
import asyncio

logger = logging.getLogger(__name__)

class SentimentAnalyzer:
    """Multi-model sentiment analysis system with BERT integration support"""
    
    def __init__(self, use_bert: bool = False):
        self.positive_words = self._load_positive_words()
        self.negative_words = self._load_negative_words()
        self.crisis_keywords = self._load_crisis_keywords()
        self.use_bert = use_bert
        
        # Try to initialize BERT analyzer if requested
        self.bert_analyzer = None
        if use_bert:
            try:
                from .bert_analyzer import BERTSentimentAnalyzer
                self.bert_analyzer = BERTSentimentAnalyzer()
                logger.info("BERT analyzer initialized successfully")
            except ImportError:
                logger.warning("BERT analyzer not available, using fallback")
                self.bert_analyzer = None
        
    def _load_positive_words(self) -> set:
        """Load positive sentiment keywords"""
        return {
            'amazing', 'awesome', 'excellent', 'fantastic', 'great', 'love', 'perfect',
            'wonderful', 'outstanding', 'brilliant', 'superb', 'incredible', 'marvelous',
            'exceptional', 'remarkable', 'impressive', 'delighted', 'satisfied', 'happy',
            'pleased', 'recommend', 'best', 'good', 'nice', 'beautiful', 'gorgeous',
            'revolutionary', 'cutting-edge', 'innovative', 'breakthrough', 'stunning'
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
        """Main keyword-based sentiment analysis method"""
        try:
            text_lower = text.lower()
            words = set(re.findall(r'\b\w+\b', text_lower))
            
            positive_matches = len(words.intersection(self.positive_words))
            negative_matches = len(words.intersection(self.negative_words))
            crisis_matches = len(words.intersection(self.crisis_keywords))
            
            # Calculate sentiment score based on keyword matches
            total_matches = positive_matches + negative_matches
            if total_matches > 0:
                polarity = (positive_matches - negative_matches) / total_matches
                sentiment_score = (polarity + 1) / 2  # Convert to 0-1 scale
            else:
                polarity = 0.0
                sentiment_score = 0.5  # Neutral
            
            # Apply keyword boosts
            if positive_matches > negative_matches:
                sentiment_score = max(sentiment_score, 0.6 + positive_matches * 0.05)
            elif negative_matches > positive_matches:
                sentiment_score = min(sentiment_score, 0.4 - negative_matches * 0.05)
            
            # Crisis keywords override sentiment
            if crisis_matches > 0:
                sentiment_score = min(sentiment_score, 0.2)
            
            # Clamp score between 0 and 1
            sentiment_score = max(0.0, min(1.0, sentiment_score))
            
            # Determine label
            if sentiment_score > 0.6:
                label = "positive"
            elif sentiment_score < 0.4:
                label = "negative"
            else:
                label = "neutral"
            
            # Calculate confidence based on keyword strength
            confidence = min(0.9, (total_matches + crisis_matches) * 0.15)
            
            return {
                'sentiment_score': round(sentiment_score, 3),
                'sentiment_label': label,
                'confidence': round(confidence, 3),
                'crisis_indicators': crisis_matches,
                'positive_keywords': positive_matches,
                'negative_keywords': negative_matches,
                'polarity': round(polarity, 3),
                'model': 'hybrid_keyword'
            }
            
        except Exception as e:
            logger.error(f"Sentiment analysis failed: {e}")
            return self._default_sentiment()
    
    async def analyze_best_available(self, text: str) -> Dict:
        """Use the best available model (BERT if available, otherwise hybrid)"""
        if self.bert_analyzer and hasattr(self.bert_analyzer, 'available') and self.bert_analyzer.available:
            try:
                return await self.analyze_ensemble(text)
            except Exception as e:
                logger.warning(f"BERT analysis failed, falling back to hybrid: {e}")
                return self.analyze_hybrid(text)
        else:
            return self.analyze_hybrid(text)
    
    async def analyze_ensemble(self, text: str) -> Dict:
        """Ensemble method combining keyword-based and BERT analysis"""
        try:
            # Get keyword-based result
            keyword_result = self.analyze_hybrid(text)
            
            # Get BERT result if available
            if self.bert_analyzer and hasattr(self.bert_analyzer, 'analyze_sentiment'):
                try:
                    bert_result = await self.bert_analyzer.analyze_sentiment(text)
                    
                    # Combine results with weighted voting
                    bert_weight = 0.7
                    keyword_weight = 0.3
                    
                    combined_score = (
                        bert_result['sentiment_score'] * bert_weight +
                        keyword_result['sentiment_score'] * keyword_weight
                    )
                    
                    # Use higher confidence
                    final_confidence = max(bert_result['confidence'], keyword_result['confidence'])
                    
                    # Determine final label
                    if combined_score > 0.65:
                        final_label = "positive"
                    elif combined_score < 0.35:
                        final_label = "negative"
                    else:
                        final_label = "neutral"
                    
                    return {
                        'sentiment_score': round(combined_score, 3),
                        'sentiment_label': final_label,
                        'confidence': round(final_confidence, 3),
                        'bert_score': bert_result['sentiment_score'],
                        'keyword_score': keyword_result['sentiment_score'],
                        'crisis_indicators': keyword_result['crisis_indicators'],
                        'model': 'ensemble_bert_keyword',
                        'bert_details': bert_result
                    }
                except Exception as e:
                    logger.warning(f"BERT analysis failed in ensemble: {e}")
                    return keyword_result
            else:
                # Fallback to keyword-based only
                return keyword_result
                
        except Exception as e:
            logger.error(f"Ensemble analysis failed: {e}")
            return self._default_sentiment()
    
    def _default_sentiment(self) -> Dict:
        """Default sentiment when analysis fails"""
        return {
            'sentiment_score': 0.5,
            'sentiment_label': 'neutral',
            'confidence': 0.0,
            'crisis_indicators': 0,
            'model': 'default'
        }
