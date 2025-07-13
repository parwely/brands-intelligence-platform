# backend/app/ml/sentiment/analyzer.py
from typing import Dict, List
from textblob import TextBlob
import logging
import re
from ..preprocessing.text_cleaner import TextPreprocessor

logger = logging.getLogger(__name__)

# Import BERT analyzer (optional dependency)
try:
    from .bert_analyzer import BERTSentimentAnalyzer
    BERT_AVAILABLE = True
except ImportError as e:
    BERT_AVAILABLE = False
    logger.warning(f"BERT analyzer not available: {e}")

class SentimentAnalyzer:
    """Multi-model sentiment analysis system with BERT integration"""
    
    def __init__(self, use_bert: bool = True):
        self.preprocessor = TextPreprocessor()
        self.positive_words = self._load_positive_words()
        self.negative_words = self._load_negative_words()
        self.crisis_keywords = self._load_crisis_keywords()
        
        # Initialize BERT analyzer if available and requested
        self.bert_analyzer = None
        if use_bert and BERT_AVAILABLE:
            try:
                self.bert_analyzer = BERTSentimentAnalyzer()
                logger.info("BERT analyzer initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize BERT analyzer: {e}")
                self.bert_analyzer = None
        else:
            logger.info("BERT analyzer disabled or not available")

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
            # Simple sentiment scoring without TextBlob dependencies
            polarity = 0.0
            
            # Use our keyword-based approach as primary
            text_lower = text.lower()
            words = set(re.findall(r'\b\w+\b', text_lower))
            
            positive_matches = len(words.intersection(self.positive_words))
            negative_matches = len(words.intersection(self.negative_words))
            crisis_matches = len(words.intersection(self.crisis_keywords))
            
            # Calculate sentiment score
            total_matches = positive_matches + negative_matches
            if total_matches > 0:
                polarity = (positive_matches - negative_matches) / total_matches
            
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
    
    async def analyze_bert(self, text: str) -> Dict:
        """BERT-based sentiment analysis"""
        if not self.bert_analyzer:
            return self._default_sentiment()
        
        try:
            return await self.bert_analyzer.analyze_sentiment(text)
        except Exception as e:
            logger.error(f"BERT analysis failed: {e}")
            return self._default_sentiment()

    async def analyze_ensemble(self, text: str) -> Dict:
        """Ensemble method combining TextBlob, Keywords, and BERT"""
        try:
            # Get results from all models
            textblob_result = self.analyze_textblob(text)
            keyword_result = self.analyze_keyword_based(text)
            
            # Get BERT result if available
            bert_result = None
            if self.bert_analyzer:
                bert_result = await self.analyze_bert(text)
            
            # Combine results with weighted voting
            if bert_result and 'error' not in bert_result:
                # BERT + Hybrid approach (BERT gets higher weight due to superior performance)
                bert_weight = 0.6
                textblob_weight = 0.25
                keyword_weight = 0.15
                
                combined_score = (
                    bert_result['sentiment_score'] * bert_weight +
                    textblob_result['sentiment_score'] * textblob_weight +
                    keyword_result['sentiment_score'] * keyword_weight
                )
                
                # Use highest confidence for final label
                best_confidence = max(
                    bert_result['confidence'],
                    textblob_result['confidence'],
                    keyword_result['confidence']
                )
                
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
                    'confidence': round(best_confidence, 3),
                    'bert_score': bert_result['sentiment_score'],
                    'textblob_score': textblob_result['sentiment_score'],
                    'keyword_score': keyword_result['sentiment_score'],
                    'crisis_indicators': keyword_result.get('crisis_keywords', 0),
                    'model': 'ensemble_with_bert',
                    'bert_details': bert_result
                }
            else:
                # Fallback to hybrid without BERT
                return self.analyze_hybrid(text)
                
        except Exception as e:
            logger.error(f"Ensemble analysis failed: {e}")
            return self._default_sentiment()

    async def analyze_best_available(self, text: str) -> Dict:
        """Use the best available model (BERT if available, otherwise hybrid)"""
        if self.bert_analyzer:
            return await self.analyze_ensemble(text)
        else:
            return self.analyze_hybrid(text)

    def analyze_textblob(self, text: str) -> Dict:
        """TextBlob-based sentiment analysis"""
        try:
            # Fallback to simple rule-based approach instead of TextBlob
            text_lower = text.lower()
            words = set(re.findall(r'\b\w+\b', text_lower))
            
            positive_matches = len(words.intersection(self.positive_words))
            negative_matches = len(words.intersection(self.negative_words))
            
            if positive_matches + negative_matches == 0:
                polarity = 0.0
                subjectivity = 0.5
            else:
                polarity = (positive_matches - negative_matches) / (positive_matches + negative_matches)
                subjectivity = min(1.0, (positive_matches + negative_matches) / len(words)) if words else 0.5
            
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
        words = set(re.findall(r'\b\w+\b', text_lower))
        
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
    
    def _default_sentiment(self) -> Dict:
        """Default sentiment when analysis fails"""
        return {
            'sentiment_score': 0.5,
            'sentiment_label': 'neutral',
            'confidence': 0.0,
            'model': 'default'
        }