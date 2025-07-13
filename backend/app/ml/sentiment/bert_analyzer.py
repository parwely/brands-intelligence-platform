# backend/app/ml/sentiment/bert_analyzer.py
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
from typing import Dict, List, Optional
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor
import numpy as np

# Import cache service (optional)
try:
    from ...core.cache import cache_service
    CACHE_AVAILABLE = True
except ImportError:
    CACHE_AVAILABLE = False

logger = logging.getLogger(__name__)

class BERTSentimentAnalyzer:
    """BERT-based sentiment analysis using pre-trained transformers with caching"""
    
    def __init__(self, model_name: str = "nlptown/bert-base-multilingual-uncased-sentiment"):
        """
        Initialize BERT sentiment analyzer
        
        Models to consider:
        - nlptown/bert-base-multilingual-uncased-sentiment (5-star rating)
        - cardiffnlp/twitter-roberta-base-sentiment-latest (positive/negative/neutral)
        - finiteautomata/bertweet-base-sentiment-analysis (Twitter-specific)
        """
        self.model_name = model_name
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.tokenizer = None
        self.model = None
        self.pipeline = None
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.use_cache = CACHE_AVAILABLE
        self._load_model()
        
    def _load_model(self):
        """Load BERT model and tokenizer"""
        try:
            logger.info(f"Loading BERT model: {self.model_name}")
            
            # Load tokenizer and model
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(self.model_name)
            
            # Move model to device
            self.model.to(self.device)
            self.model.eval()
            
            # Create pipeline for easier inference
            self.pipeline = pipeline(
                "sentiment-analysis",
                model=self.model,
                tokenizer=self.tokenizer,
                device=0 if self.device == "cuda" else -1,
                return_all_scores=True
            )
            
            logger.info(f"BERT model loaded successfully on {self.device}")
            
        except Exception as e:
            logger.error(f"Failed to load BERT model: {e}")
            self.pipeline = None
    
    async def analyze_sentiment(self, text: str) -> Dict:
        """
        Analyze sentiment using BERT model with caching
        
        Returns:
            Dict with sentiment_score, sentiment_label, confidence, and model_info
        """
        if not self.pipeline:
            return self._fallback_response()
        
        # Check cache first
        if self.use_cache:
            try:
                cached_result = await cache_service.get_bert_cache(text, self.model_name)
                if cached_result:
                    cached_result['cache_hit'] = True
                    return cached_result
            except Exception as e:
                logger.warning(f"Cache read failed: {e}")
        
        try:
            # Run inference in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                self.executor, 
                self._run_inference, 
                text
            )
            
            analysis_result = self._process_bert_output(result, text)
            analysis_result['cache_hit'] = False
            
            # Cache the result
            if self.use_cache:
                try:
                    await cache_service.set_bert_cache(text, self.model_name, analysis_result)
                except Exception as e:
                    logger.warning(f"Cache write failed: {e}")
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"BERT inference failed: {e}")
            return self._fallback_response()
    
    def _run_inference(self, text: str) -> List[Dict]:
        """Run BERT inference (synchronous)"""
        # Truncate text to model's max length
        max_length = self.tokenizer.model_max_length
        if len(text) > max_length:
            text = text[:max_length-10] + "..."
        
        return self.pipeline(text)
    
    def _process_bert_output(self, bert_output: List[Dict], original_text: str) -> Dict:
        """Process BERT model output into standardized format"""
        if not bert_output or len(bert_output) == 0:
            return self._fallback_response()
        
        # Extract scores for each label
        scores = {item['label']: item['score'] for item in bert_output}
        
        # Determine the predicted label and confidence
        predicted = max(bert_output, key=lambda x: x['score'])
        predicted_label = predicted['label']
        confidence = predicted['score']
        
        # Convert to standardized sentiment score (0-1 scale)
        sentiment_score = self._convert_to_standard_score(scores, predicted_label)
        
        # Map BERT labels to our standard labels
        standard_label = self._map_bert_label(predicted_label, sentiment_score)
        
        # Calculate additional metrics
        subjectivity = self._estimate_subjectivity(scores)
        
        return {
            'sentiment_score': round(sentiment_score, 3),
            'sentiment_label': standard_label,
            'confidence': round(confidence, 3),
            'subjectivity': round(subjectivity, 3),
            'bert_scores': scores,
            'bert_predicted_label': predicted_label,
            'model': 'bert',
            'model_name': self.model_name,
            'device': self.device
        }
    
    def _convert_to_standard_score(self, scores: Dict, predicted_label: str) -> float:
        """Convert BERT scores to 0-1 sentiment scale"""
        
        # Handle different model outputs
        if 'POSITIVE' in scores and 'NEGATIVE' in scores:
            # Binary sentiment (cardiffnlp models)
            pos_score = scores.get('POSITIVE', 0)
            neg_score = scores.get('NEGATIVE', 0)
            neutral_score = scores.get('NEUTRAL', 0)
            
            if neutral_score > 0:
                # 3-class model: weight between positive and negative
                return (pos_score + neutral_score * 0.5) / (pos_score + neg_score + neutral_score)
            else:
                # 2-class model
                return pos_score / (pos_score + neg_score)
                
        elif any(label.startswith('LABEL_') for label in scores.keys()):
            # Star rating models (nlptown models) - LABEL_0 (1 star) to LABEL_4 (5 stars)
            total_score = 0
            total_weight = 0
            
            for label, score in scores.items():
                if label.startswith('LABEL_'):
                    # Extract star rating (0=1star, 1=2stars, ..., 4=5stars)
                    star_level = int(label.split('_')[1])
                    # Convert to 0-1 scale (0=1star=0.0, 4=5stars=1.0)
                    normalized_rating = star_level / 4.0
                    total_score += normalized_rating * score
                    total_weight += score
            
            return total_score / total_weight if total_weight > 0 else 0.5
        
        else:
            # Fallback: use predicted label to estimate score
            if 'positive' in predicted_label.lower():
                return 0.8
            elif 'negative' in predicted_label.lower():
                return 0.2
            else:
                return 0.5
    
    def _map_bert_label(self, bert_label: str, sentiment_score: float) -> str:
        """Map BERT label to our standard labels"""
        if sentiment_score > 0.6:
            return "positive"
        elif sentiment_score < 0.4:
            return "negative"
        else:
            return "neutral"
    
    def _estimate_subjectivity(self, scores: Dict) -> float:
        """Estimate subjectivity based on score distribution"""
        # Calculate entropy of the distribution
        values = list(scores.values())
        if len(values) <= 1:
            return 0.5
        
        # Normalize to probabilities
        total = sum(values)
        probs = [v/total for v in values]
        
        # Calculate entropy (higher entropy = more objective/neutral)
        entropy = -sum(p * np.log2(p + 1e-10) for p in probs)
        max_entropy = np.log2(len(probs))
        
        # Convert to subjectivity (0=objective, 1=subjective)
        subjectivity = 1 - (entropy / max_entropy)
        return max(0.0, min(1.0, subjectivity))
    
    async def batch_analyze(self, texts: List[str]) -> List[Dict]:
        """Analyze multiple texts efficiently"""
        if not self.pipeline:
            return [self._fallback_response() for _ in texts]
        
        try:
            # Process in batches to avoid memory issues
            batch_size = 16
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
            'subjectivity': 0.5,
            'model': 'bert_fallback',
            'error': 'BERT model unavailable'
        }
    
    def get_model_info(self) -> Dict:
        """Get information about the loaded BERT model"""
        return {
            'model_name': self.model_name,
            'device': self.device,
            'available': self.pipeline is not None,
            'model_type': 'transformer',
            'capabilities': ['sentiment_analysis', 'confidence_scoring', 'batch_processing'],
            'max_length': self.tokenizer.model_max_length if self.tokenizer else None
        }
    
    def __del__(self):
        """Clean up thread pool on deletion"""
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=False)

# Test function
async def test_bert_analyzer():
    """Test BERT analyzer with sample texts"""
    analyzer = BERTSentimentAnalyzer()
    
    test_texts = [
        "I absolutely love this product! Amazing quality!",
        "This is terrible. Worst purchase ever!",
        "The product is okay. Nothing special.",
        "SCAM! This company is fraudulent!",
        "Great service, fast delivery, highly recommend!"
    ]
    
    print("🤖 Testing BERT Sentiment Analyzer...")
    print("=" * 50)
    
    for i, text in enumerate(test_texts, 1):
        result = await analyzer.analyze_sentiment(text)
        print(f"\n{i}. Text: {text}")
        print(f"   BERT Result: {result['sentiment_label']} ({result['sentiment_score']:.3f})")
        print(f"   Confidence: {result['confidence']:.3f}")
        print(f"   BERT Scores: {result.get('bert_scores', {})}")
    
    # Test batch processing
    print(f"\n🚀 Testing batch processing...")
    batch_results = await analyzer.batch_analyze(test_texts)
    print(f"   Processed {len(batch_results)} texts in batch")
    
    # Model info
    model_info = analyzer.get_model_info()
    print(f"\n📊 Model Info: {model_info}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_bert_analyzer())
