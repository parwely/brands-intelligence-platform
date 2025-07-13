# backend/app/ml/sentiment/bert_analyzer.py
from typing import Dict, List, Optional
import logging
import asyncio

logger = logging.getLogger(__name__)

class BERTSentimentAnalyzer:
    """BERT-based sentiment analysis with fallback support"""
    
    def __init__(self, model_name: str = "nlptown/bert-base-multilingual-uncased-sentiment"):
        self.model_name = model_name
        self.available = False
        self.pipeline = None
        self.device = "cpu"  # Default to CPU for compatibility
        
        try:
            # Try to import transformers
            import torch
            from transformers import pipeline
            
            # Initialize the pipeline
            self.pipeline = pipeline(
                "sentiment-analysis",
                model=self.model_name,
                device=-1,  # Use CPU
                return_all_scores=True
            )
            self.available = True
            logger.info(f"BERT model {self.model_name} loaded successfully")
            
        except ImportError as e:
            logger.warning(f"Transformers not available: {e}")
            self.available = False
        except Exception as e:
            logger.warning(f"Failed to load BERT model: {e}")
            self.available = False
    
    async def analyze_sentiment(self, text: str) -> Dict:
        """Analyze sentiment using BERT model"""
        if not self.available or not self.pipeline:
            return self._fallback_response()
        
        try:
            # Run inference in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, self._run_inference, text)
            
            return self._process_bert_output(result, text)
            
        except Exception as e:
            logger.error(f"BERT inference failed: {e}")
            return self._fallback_response()
    
    def _run_inference(self, text: str) -> List:
        """Run BERT inference (synchronous)"""
        try:
            # Truncate text if too long
            max_length = 512
            if len(text) > max_length:
                text = text[:max_length-10] + "..."
            
            if self.pipeline is None:
                return []
            
            results = self.pipeline(text)
            return results if isinstance(results, list) else [results]
            
        except Exception as e:
            logger.error(f"BERT inference failed: {e}")
            return []
    
    def _process_bert_output(self, bert_output: List, original_text: str) -> Dict:
        """Process BERT model output into standardized format"""
        if not bert_output:
            return self._fallback_response()
        
        try:
            # Handle different model output formats
            if isinstance(bert_output[0], list):
                # Multiple scores per input
                scores = {item['label']: item['score'] for item in bert_output[0]}
            else:
                # Single prediction
                scores = {bert_output[0]['label']: bert_output[0]['score']}
            
            # Find the predicted label and confidence
            predicted = max(scores.items(), key=lambda x: x[1])
            predicted_label = predicted[0]
            confidence = predicted[1]
            
            # Convert to standardized sentiment score (0-1 scale)
            sentiment_score = self._convert_to_standard_score(scores, predicted_label)
            
            # Map BERT labels to our standard labels
            standard_label = self._map_bert_label(predicted_label, sentiment_score)
            
            return {
                'sentiment_score': round(sentiment_score, 3),
                'sentiment_label': standard_label,
                'confidence': round(confidence, 3),
                'bert_scores': scores,
                'bert_predicted_label': predicted_label,
                'model': 'bert',
                'model_name': self.model_name
            }
            
        except Exception as e:
            logger.error(f"BERT output processing failed: {e}")
            return self._fallback_response()
    
    def _convert_to_standard_score(self, scores: Dict, predicted_label: str) -> float:
        """Convert BERT scores to 0-1 sentiment scale"""
        try:
            # Handle different model outputs
            if 'POSITIVE' in scores and 'NEGATIVE' in scores:
                # Binary sentiment model
                pos_score = scores.get('POSITIVE', 0)
                neg_score = scores.get('NEGATIVE', 0)
                neutral_score = scores.get('NEUTRAL', 0)
                
                if neutral_score > 0:
                    # 3-class model
                    return (pos_score + neutral_score * 0.5) / (pos_score + neg_score + neutral_score)
                else:
                    # 2-class model
                    return pos_score / (pos_score + neg_score) if (pos_score + neg_score) > 0 else 0.5
                    
            elif any(label.startswith('LABEL_') for label in scores.keys()):
                # Star rating models (LABEL_0=1star to LABEL_4=5stars)
                total_score = 0
                total_weight = 0
                
                for label, score in scores.items():
                    if label.startswith('LABEL_'):
                        star_level = int(label.split('_')[1])
                        normalized_rating = star_level / 4.0  # Convert to 0-1 scale
                        total_score += normalized_rating * score
                        total_weight += score
                
                return total_score / total_weight if total_weight > 0 else 0.5
            
            else:
                # Fallback based on predicted label
                if 'positive' in predicted_label.lower():
                    return 0.8
                elif 'negative' in predicted_label.lower():
                    return 0.2
                else:
                    return 0.5
                    
        except Exception as e:
            logger.warning(f"Score conversion failed: {e}")
            return 0.5
    
    def _map_bert_label(self, bert_label: str, sentiment_score: float) -> str:
        """Map BERT label to our standard labels"""
        if sentiment_score > 0.6:
            return "positive"
        elif sentiment_score < 0.4:
            return "negative"
        else:
            return "neutral"
    
    async def batch_analyze(self, texts: List[str]) -> List[Dict]:
        """Analyze multiple texts efficiently"""
        if not self.available:
            return [self._fallback_response() for _ in texts]
        
        try:
            # Process in batches to avoid memory issues
            batch_size = 8
            results = []
            
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                batch_results = await asyncio.gather(*[
                    self.analyze_sentiment(text) for text in batch
                ])
                results.extend(batch_results)
            
            return results
            
        except Exception as e:
            logger.error(f"BERT batch analysis failed: {e}")
            return [self._fallback_response() for _ in texts]
    
    def _fallback_response(self) -> Dict:
        """Fallback response when BERT is unavailable"""
        return {
            'sentiment_score': 0.5,
            'sentiment_label': 'neutral',
            'confidence': 0.0,
            'model': 'bert_fallback',
            'error': 'BERT model unavailable'
        }
    
    def get_model_info(self) -> Dict:
        """Get information about the loaded BERT model"""
        return {
            'model_name': self.model_name,
            'available': self.available,
            'device': self.device,
            'model_type': 'transformer',
            'capabilities': ['sentiment_analysis', 'confidence_scoring', 'batch_processing']
        }
