# backend/app/services/ml_service.py
from typing import Dict, List
import logging
import asyncio
from ..ml.sentiment.analyzer import SentimentAnalyzer
from ..ml.preprocessing.text_cleaner import TextPreprocessor

# Import cache service (optional)
try:
    from ..core.cache import cache_service
    CACHE_AVAILABLE = True
except ImportError:
    CACHE_AVAILABLE = False
    cache_service = None

logger = logging.getLogger(__name__)

class MLService:
    """Main ML service orchestrating all AI operations with caching"""
    
    def __init__(self):
        try:
            self.sentiment_analyzer = SentimentAnalyzer(use_bert=True)
            self.preprocessor = TextPreprocessor()
            self._model_version = "2.0.0"  # Updated for BERT integration
            self.use_cache = CACHE_AVAILABLE
            logger.info("ML Service initialized successfully with BERT support")
        except Exception as e:
            logger.error(f"Failed to initialize ML Service: {e}")
            raise
        
    async def analyze_mention_sentiment(self, text: str, use_cache: bool = True) -> Dict:
        """Comprehensive analysis of a single mention with caching"""
        try:
            # Check cache first
            if use_cache and self.use_cache:
                try:
                    cached_result = await cache_service.get_sentiment_cache(text)
                    if cached_result:
                        cached_result['cache_hit'] = True
                        return cached_result
                except Exception as e:
                    logger.warning(f"Cache read failed: {e}")
            
            # Get text features
            features = self.preprocessor.extract_features(text)
            
            # Analyze sentiment with best available model (BERT or hybrid)
            sentiment = await self.sentiment_analyzer.analyze_best_available(text)
            
            # Calculate crisis probability
            crisis_prob = await self._calculate_crisis_probability(sentiment, features)
            
            # Calculate urgency score
            urgency = self._calculate_urgency_score(sentiment, features)
            
            result = {
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
                    'model': sentiment.get('model', 'hybrid'),
                    'version': self._model_version,
                    'textblob_score': sentiment.get('textblob_score'),
                    'keyword_score': sentiment.get('keyword_score'),
                    'bert_details': sentiment.get('bert_details'),
                    'cache_hit': False
                }
            }
            
            # Cache the result
            if use_cache and self.use_cache:
                try:
                    await cache_service.set_sentiment_cache(text, result)
                except Exception as e:
                    logger.warning(f"Cache write failed: {e}")
            
            return result
            
        except Exception as e:
            logger.error(f"ML analysis failed for text '{text[:50]}...': {e}")
            return self._error_response()
    
    async def batch_analyze_mentions(self, texts: List[str], use_cache: bool = True) -> List[Dict]:
        """Analyze multiple mentions efficiently with intelligent caching"""
        try:
            # For batch processing, handle cache checks efficiently
            if use_cache and self.use_cache:
                cached_results = {}
                uncached_texts = []
                
                # Check which texts are already cached
                for i, text in enumerate(texts):
                    try:
                        cached_result = await cache_service.get_sentiment_cache(text)
                        if cached_result:
                            cached_result['cache_hit'] = True
                            cached_results[i] = cached_result
                        else:
                            uncached_texts.append((i, text))
                    except Exception as e:
                        logger.warning(f"Cache check failed for text {i}: {e}")
                        uncached_texts.append((i, text))
                
                # Process uncached texts
                uncached_tasks = [
                    self.analyze_mention_sentiment(text, use_cache=False) 
                    for _, text in uncached_texts
                ]
                uncached_results = await asyncio.gather(*uncached_tasks)
                
                # Combine results in original order
                results = []
                for i in range(len(texts)):
                    if i in cached_results:
                        results.append(cached_results[i])
                    else:
                        # Find the corresponding result from uncached_results
                        uncached_index = next(
                            idx for idx, (original_idx, _) in enumerate(uncached_texts) 
                            if original_idx == i
                        )
                        results.append(uncached_results[uncached_index])
                
                return results
            else:
                # No caching - process all
                tasks = [self.analyze_mention_sentiment(text, use_cache=False) for text in texts]
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
        """Get information about loaded models with cache stats"""
        model_info = {
            'version': self._model_version,
            'models': {},
            'capabilities': [
                'Sentiment Analysis',
                'Crisis Detection', 
                'Urgency Scoring',
                'Text Feature Extraction',
                'BERT Integration',
                'Ensemble Analysis'
            ],
            'languages': ['English'],
            'status': 'active',
            'cache': {
                'available': self.use_cache,
                'stats': {}
            }
        }
        
        # Get sentiment analyzer info
        if hasattr(self.sentiment_analyzer, 'bert_analyzer') and self.sentiment_analyzer.bert_analyzer:
            bert_info = self.sentiment_analyzer.bert_analyzer.get_model_info()
            model_info['models']['sentiment'] = f"Ensemble (BERT + Hybrid) - {bert_info['model_name']}"
            model_info['models']['bert'] = bert_info
        else:
            model_info['models']['sentiment'] = 'Hybrid (TextBlob + Keywords)'
        
        model_info['models']['preprocessing'] = 'NLTK + Custom Rules'
        model_info['models']['crisis_detection'] = 'Rule-based Algorithm'
        
        # Get cache stats
        if self.use_cache:
            try:
                cache_stats = await cache_service.get_cache_stats()
                model_info['cache']['stats'] = cache_stats
            except Exception as e:
                logger.warning(f"Failed to get cache stats: {e}")
                model_info['cache']['stats'] = {"error": str(e)}
        
        return model_info
    
    async def clear_cache(self, pattern: str = "*") -> Dict:
        """Clear ML cache with optional pattern"""
        if not self.use_cache:
            return {"success": False, "error": "Cache not available"}
        
        try:
            if pattern == "*":
                # Clear all ML-related caches
                sentiment_cleared = await cache_service.invalidate_pattern("sentiment:*")
                bert_cleared = await cache_service.invalidate_pattern("bert:*")
                analytics_cleared = await cache_service.invalidate_pattern("analytics:*")
                
                total_cleared = sentiment_cleared + bert_cleared + analytics_cleared
            else:
                total_cleared = await cache_service.invalidate_pattern(pattern)
            
            return {
                "success": True,
                "cleared_keys": total_cleared,
                "pattern": pattern
            }
        except Exception as e:
            logger.error(f"Cache clear failed: {e}")
            return {"success": False, "error": str(e)}

# Global ML service instance
ml_service = MLService()