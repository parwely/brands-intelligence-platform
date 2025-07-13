# backend/app/services/ml_service.py
from typing import Dict, List, Optional
import logging
import asyncio
from datetime import datetime
from ..ml.sentiment.analyzer import SentimentAnalyzer
from ..ml.sentiment.bert_analyzer import BERTSentimentAnalyzer
from ..ml.sentiment.crisis_detector import CrisisDetector
# from ..ml.preprocessing.text_cleaner import TextPreprocessor  # Temporarily disabled due to encoding issue

logger = logging.getLogger(__name__)

class MLService:
    """Advanced ML service with sentiment analysis, crisis detection, and real-time processing"""
    
    def __init__(self):
        # Initialize ML components with error handling
        try:
            self.sentiment_analyzer = SentimentAnalyzer()
            logger.info("SentimentAnalyzer initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize SentimentAnalyzer: {e}")
            self.sentiment_analyzer = None
        
        try:
            self.bert_analyzer = BERTSentimentAnalyzer()
            logger.info("BERTSentimentAnalyzer initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize BERTSentimentAnalyzer: {e}")
            self.bert_analyzer = None
        
        try:
            self.crisis_detector = CrisisDetector()
            logger.info("CrisisDetector initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize CrisisDetector: {e}")
            self.crisis_detector = None
        
        try:
            # self.preprocessor = TextPreprocessor()  # Temporarily disabled
            self.preprocessor = None
            logger.info("TextPreprocessor temporarily disabled due to encoding issue")
        except Exception as e:
            logger.error(f"Failed to initialize TextPreprocessor: {e}")
            self.preprocessor = None
    
    async def extract_features(self, text: str) -> Dict:
        """Extract comprehensive text features using the preprocessor"""
        try:
            if self.preprocessor is not None:
                # When preprocessor is available, call its extract_features method
                # Note: This would be async when preprocessor is properly implemented
                return self.preprocessor.extract_features(text)
            else:
                return self._extract_basic_features(text)
        except Exception as e:
            logger.error(f"Feature extraction failed: {e}")
            return self._extract_basic_features(text)
    
    def _extract_basic_features(self, text: str) -> Dict:
        """Fallback feature extraction"""
        return {
            'char_count': len(text),
            'word_count': len(text.split()),
            'sentence_count': len([s for s in text.split('.') if s.strip()]),
            'uppercase_ratio': sum(1 for c in text if c.isupper()) / len(text) if text else 0,
            'punctuation_count': sum(1 for c in text if not c.isalnum() and not c.isspace()),
            'exclamation_count': text.count('!'),
            'question_count': text.count('?')
        }
    
    async def analyze_mention_sentiment(self, text: str, use_bert: bool = True) -> Dict:
        """Analyze sentiment of a single mention with optional BERT analysis"""
        try:
            if not text or not isinstance(text, str):
                return self._fallback_sentiment_response("Invalid text input")
            
            # Get base sentiment analysis
            base_result = {}
            if self.sentiment_analyzer:
                try:
                    base_result = await self.sentiment_analyzer.analyze_best_available(text)
                except Exception as e:
                    logger.error(f"Base sentiment analysis failed: {e}")
                    base_result = self._fallback_sentiment_response("Base analysis failed")
            
            # Add BERT analysis if requested and available
            bert_result = {}
            if use_bert and self.bert_analyzer and self.bert_analyzer.available:
                try:
                    bert_result = await self.bert_analyzer.analyze_sentiment(text)
                except Exception as e:
                    logger.error(f"BERT sentiment analysis failed: {e}")
                    bert_result = {'error': 'BERT analysis failed'}
            
            # Combine results
            combined_result = {
                'text': text[:200] + '...' if len(text) > 200 else text,
                'base_analysis': base_result,
                'bert_analysis': bert_result if bert_result else None,
                'timestamp': datetime.now().isoformat(),
                'processing_time_ms': 0  # Placeholder
            }
            
            # Use best available result
            if bert_result and 'sentiment_score' in bert_result:
                combined_result['final_sentiment'] = bert_result
            elif base_result and 'sentiment_score' in base_result:
                combined_result['final_sentiment'] = base_result
            else:
                combined_result['final_sentiment'] = self._fallback_sentiment_response("All analysis failed")
            
            return combined_result
            
        except Exception as e:
            logger.error(f"Mention sentiment analysis failed: {e}")
            return {
                'error': str(e),
                'final_sentiment': self._fallback_sentiment_response("Analysis error"),
                'timestamp': datetime.now().isoformat()
            }
    
    async def analyze_crisis(self, mentions: List[Dict], brand_name: str) -> Dict:
        """Analyze crisis indicators in mentions for a brand"""
        try:
            if not mentions or not brand_name:
                return {'crisis_level': 'none', 'crisis_score': 0.0, 'error': 'Invalid input'}
            
            if not self.crisis_detector:
                return {'crisis_level': 'none', 'crisis_score': 0.0, 'error': 'Crisis detector unavailable'}
            
            # Analyze crisis in batch
            crisis_results = await self.crisis_detector.batch_detect_crisis(mentions, brand_name)
            
            # Calculate aggregate crisis metrics
            if crisis_results:
                scores = [r.get('crisis_score', 0) for r in crisis_results]
                levels = [r.get('crisis_level', 'none') for r in crisis_results]
                
                max_score = max(scores) if scores else 0.0
                avg_score = sum(scores) / len(scores) if scores else 0.0
                
                # Determine overall crisis level
                level_priority = {'critical': 4, 'major': 3, 'moderate': 2, 'minor': 1, 'none': 0}
                max_level = max(levels, key=lambda x: level_priority.get(x, 0))
                
                # Get brand summary
                brand_summary = self.crisis_detector.get_brand_crisis_summary(brand_name)
                
                return {
                    'brand': brand_name,
                    'overall_crisis_level': max_level,
                    'max_crisis_score': round(max_score, 3),
                    'avg_crisis_score': round(avg_score, 3),
                    'total_mentions_analyzed': len(mentions),
                    'crisis_mentions_count': len([r for r in crisis_results if r.get('crisis_level') != 'none']),
                    'individual_results': crisis_results,
                    'brand_summary': brand_summary,
                    'timestamp': datetime.now().isoformat()
                }
            else:
                return {'crisis_level': 'none', 'crisis_score': 0.0, 'error': 'No results from crisis analysis'}
                
        except Exception as e:
            logger.error(f"Crisis analysis failed: {e}")
            return {
                'error': str(e),
                'crisis_level': 'none',
                'crisis_score': 0.0,
                'timestamp': datetime.now().isoformat()
            }
    
    async def batch_analyze_mentions(self, mentions: List[Dict], brand_name: str, include_bert: bool = True) -> Dict:
        """Analyze multiple mentions for sentiment and crisis indicators"""
        try:
            if not mentions:
                return {'error': 'No mentions provided', 'results': []}
            
            # Extract texts for analysis
            texts = []
            for mention in mentions:
                text = mention.get('text', mention.get('content', ''))
                if text:
                    texts.append(text)
            
            if not texts:
                return {'error': 'No valid texts found in mentions', 'results': []}
            
            # Parallel sentiment analysis
            sentiment_tasks = [
                self.analyze_mention_sentiment(text, use_bert=include_bert) 
                for text in texts
            ]
            sentiment_results = await asyncio.gather(*sentiment_tasks, return_exceptions=True)
            
            # Crisis analysis
            crisis_result = await self.analyze_crisis(mentions, brand_name)
            
            # Combine results with mention metadata
            combined_results = []
            for i, mention in enumerate(mentions):
                if i < len(sentiment_results):
                    sentiment = sentiment_results[i]
                    if isinstance(sentiment, Exception):
                        sentiment = {'error': str(sentiment)}
                    
                    combined_results.append({
                        'mention_id': mention.get('id', f'mention_{i}'),
                        'text': mention.get('text', mention.get('content', '')),
                        'sentiment_analysis': sentiment,
                        'source': mention.get('source', 'unknown'),
                        'timestamp': mention.get('timestamp', datetime.now().isoformat())
                    })
            
            return {
                'brand': brand_name,
                'total_mentions': len(mentions),
                'analyzed_mentions': len(combined_results),
                'sentiment_results': combined_results,
                'crisis_analysis': crisis_result,
                'processing_timestamp': datetime.now().isoformat(),
                'bert_used': include_bert and self.bert_analyzer and self.bert_analyzer.available
            }
            
        except Exception as e:
            logger.error(f"Batch analysis failed: {e}")
            return {
                'error': str(e),
                'brand': brand_name,
                'total_mentions': len(mentions) if mentions else 0,
                'results': [],
                'timestamp': datetime.now().isoformat()
            }
    
    async def analyze_brand_health(self, brand_name: str, mentions: List[Dict], time_window_hours: int = 24) -> Dict:
        """Comprehensive brand health analysis"""
        try:
            if not mentions:
                return self._empty_brand_health(brand_name, "No mentions provided")
            
            # Batch analysis
            analysis_result = await self.batch_analyze_mentions(mentions, brand_name, include_bert=True)
            
            if 'error' in analysis_result:
                return self._empty_brand_health(brand_name, analysis_result['error'])
            
            # Extract sentiment scores
            sentiment_scores = []
            sentiment_labels = []
            
            for result in analysis_result.get('sentiment_results', []):
                sentiment = result.get('sentiment_analysis', {}).get('final_sentiment', {})
                if 'sentiment_score' in sentiment:
                    sentiment_scores.append(sentiment['sentiment_score'])
                    sentiment_labels.append(sentiment.get('sentiment_label', 'neutral'))
            
            # Calculate metrics
            if sentiment_scores:
                avg_sentiment = sum(sentiment_scores) / len(sentiment_scores)
                positive_ratio = len([s for s in sentiment_labels if s == 'positive']) / len(sentiment_labels)
                negative_ratio = len([s for s in sentiment_labels if s == 'negative']) / len(sentiment_labels)
                neutral_ratio = len([s for s in sentiment_labels if s == 'neutral']) / len(sentiment_labels)
            else:
                avg_sentiment = 0.5
                positive_ratio = negative_ratio = neutral_ratio = 0.0
            
            # Crisis metrics
            crisis_analysis = analysis_result.get('crisis_analysis', {})
            crisis_score = crisis_analysis.get('max_crisis_score', 0.0)
            crisis_level = crisis_analysis.get('overall_crisis_level', 'none')
            
            # Overall health score (0-100)
            health_score = self._calculate_health_score(avg_sentiment, crisis_score, positive_ratio, negative_ratio)
            
            # Health level
            health_level = self._determine_health_level(health_score)
            
            return {
                'brand': brand_name,
                'health_score': round(health_score, 1),
                'health_level': health_level,
                'sentiment_metrics': {
                    'average_sentiment': round(avg_sentiment, 3),
                    'positive_ratio': round(positive_ratio, 3),
                    'negative_ratio': round(negative_ratio, 3),
                    'neutral_ratio': round(neutral_ratio, 3),
                    'total_mentions': len(mentions)
                },
                'crisis_metrics': {
                    'crisis_score': crisis_score,
                    'crisis_level': crisis_level,
                    'crisis_mentions': crisis_analysis.get('crisis_mentions_count', 0)
                },
                'recommendations': self._generate_recommendations(health_score, crisis_level, negative_ratio),
                'analysis_timestamp': datetime.now().isoformat(),
                'time_window_hours': time_window_hours
            }
            
        except Exception as e:
            logger.error(f"Brand health analysis failed: {e}")
            return self._empty_brand_health(brand_name, str(e))
    
    def _calculate_health_score(self, avg_sentiment: float, crisis_score: float, positive_ratio: float, negative_ratio: float) -> float:
        """Calculate overall brand health score (0-100)"""
        # Base score from sentiment (0-100)
        sentiment_score = avg_sentiment * 100
        
        # Positive/negative ratio adjustment
        ratio_adjustment = (positive_ratio - negative_ratio) * 20
        
        # Crisis penalty
        crisis_penalty = crisis_score * 50
        
        # Combine factors
        health_score = sentiment_score + ratio_adjustment - crisis_penalty
        
        # Ensure score is between 0-100
        return max(0, min(100, health_score))
    
    def _determine_health_level(self, health_score: float) -> str:
        """Determine health level from score"""
        if health_score >= 80:
            return 'excellent'
        elif health_score >= 65:
            return 'good'
        elif health_score >= 50:
            return 'fair'
        elif health_score >= 35:
            return 'poor'
        else:
            return 'critical'
    
    def _generate_recommendations(self, health_score: float, crisis_level: str, negative_ratio: float) -> List[str]:
        """Generate actionable recommendations based on analysis"""
        recommendations = []
        
        if crisis_level in ['critical', 'major']:
            recommendations.append("Immediate crisis response required - engage crisis management team")
            recommendations.append("Monitor social media channels closely for emerging issues")
        
        if health_score < 50:
            recommendations.append("Improve customer service and address common complaints")
            recommendations.append("Launch positive PR campaigns to improve brand perception")
        
        if negative_ratio > 0.3:
            recommendations.append("Investigate root causes of negative sentiment")
            recommendations.append("Implement targeted customer satisfaction improvements")
        
        if health_score > 75:
            recommendations.append("Maintain current positive momentum")
            recommendations.append("Consider leveraging positive sentiment for marketing campaigns")
        
        if not recommendations:
            recommendations.append("Continue monitoring brand mentions and sentiment trends")
        
        return recommendations
    
    def _fallback_sentiment_response(self, error_msg: str) -> Dict:
        """Fallback response for sentiment analysis"""
        return {
            'sentiment_score': 0.5,
            'sentiment_label': 'neutral',
            'confidence': 0.0,
            'model': 'fallback',
            'error': error_msg
        }
    
    def _empty_brand_health(self, brand_name: str, error_msg: str) -> Dict:
        """Empty brand health response for errors"""
        return {
            'brand': brand_name,
            'health_score': 0.0,
            'health_level': 'unknown',
            'error': error_msg,
            'sentiment_metrics': {
                'average_sentiment': 0.5,
                'positive_ratio': 0.0,
                'negative_ratio': 0.0,
                'neutral_ratio': 0.0,
                'total_mentions': 0
            },
            'crisis_metrics': {
                'crisis_score': 0.0,
                'crisis_level': 'none',
                'crisis_mentions': 0
            },
            'recommendations': ["Unable to analyze - insufficient data"],
            'analysis_timestamp': datetime.now().isoformat()
        }
    
    def get_service_status(self) -> Dict:
        """Get status of all ML service components"""
        return {
            'sentiment_analyzer': self.sentiment_analyzer is not None,
            'bert_analyzer': self.bert_analyzer is not None and getattr(self.bert_analyzer, 'available', False),
            'crisis_detector': self.crisis_detector is not None,
            'text_preprocessor': self.preprocessor is not None,
            'service_healthy': all([
                self.sentiment_analyzer is not None,
                self.crisis_detector is not None,
                self.preprocessor is not None
            ]),
            'timestamp': datetime.now().isoformat()
        }
