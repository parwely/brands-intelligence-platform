# backend/app/ml/sentiment/crisis_detector.py
from typing import Dict, List, Optional, Tuple
import logging
from datetime import datetime, timedelta
import re
from collections import defaultdict, Counter
import asyncio

logger = logging.getLogger(__name__)

class CrisisDetector:
    """Multi-signal crisis detection for brand monitoring"""
    
    def __init__(self):
        # Crisis keywords by severity
        self.crisis_keywords = {
            'critical': [
                'lawsuit', 'sued', 'legal action', 'class action', 'fraud', 'scandal',
                'investigation', 'federal', 'criminal', 'indictment', 'corruption',
                'fired', 'resignation', 'stepped down', 'ousted', 'terminated',
                'data breach', 'hack', 'cyberattack', 'security breach', 'leaked',
                'toxic', 'poison', 'death', 'killed', 'died', 'fatal', 'dangerous',
                'recall', 'recalled', 'defective', 'contaminated', 'unsafe',
                'bankruptcy', 'insolvent', 'liquidation', 'chapter 11', 'bankrupt'
            ],
            'major': [
                'protest', 'boycott', 'strike', 'walkout', 'demonstration',
                'complaint', 'violated', 'violation', 'misconduct', 'inappropriate',
                'discrimination', 'harassment', 'bias', 'unfair', 'unethical',
                'controversy', 'controversial', 'outrage', 'backlash', 'criticism',
                'emergency', 'incident', 'accident', 'injury', 'hospitalized',
                'malfunction', 'failure', 'broken', 'stopped working', 'defect',
                'layoffs', 'downsizing', 'restructuring', 'closure', 'shutdown'
            ],
            'moderate': [
                'disappointed', 'concerned', 'worried', 'frustrated', 'angry',
                'problem', 'issue', 'trouble', 'difficult', 'challenging',
                'poor quality', 'bad service', 'slow response', 'unhelpful',
                'mistake', 'error', 'wrong', 'incorrect', 'miscommunication',
                'delayed', 'late', 'postponed', 'cancelled', 'unavailable',
                'expensive', 'overpriced', 'costly', 'price increase', 'surge pricing'
            ]
        }
        
        # Intensity multipliers
        self.intensity_patterns = {
            r'\b(extremely?|very|absolutely|completely|totally)\b': 1.5,
            r'\b(multiple|several|many|numerous)\b': 1.3,
            r'[A-Z]{3,}': 1.4,  # All caps words
            r'[!]{2,}': 1.2,   # Multiple exclamation marks
            r'[?]{2,}': 1.1,   # Multiple question marks
        }
        
        # Recent crisis memory for velocity tracking
        self.recent_detections = defaultdict(list)
        self.velocity_window = timedelta(hours=6)
    
    async def detect_crisis(self, text: str, brand: str, mention_time: Optional[datetime] = None) -> Dict:
        """Detect crisis signals in a single mention"""
        if mention_time is None:
            mention_time = datetime.now()
        
        # Normalize text
        text_lower = text.lower()
        
        # Base crisis signals
        keyword_signals = self._detect_keyword_signals(text_lower)
        sentiment_signals = self._detect_sentiment_signals(text)
        pattern_signals = self._detect_pattern_signals(text)
        
        # Calculate base crisis score
        base_score = self._calculate_base_score(keyword_signals, sentiment_signals, pattern_signals)
        
        # Apply intensity multipliers
        intensity_multiplier = self._calculate_intensity_multiplier(text)
        crisis_score = min(base_score * intensity_multiplier, 1.0)
        
        # Determine crisis level
        crisis_level = self._determine_crisis_level(crisis_score)
        
        # Store detection for velocity tracking
        if crisis_level != 'none':
            self.recent_detections[brand].append({
                'timestamp': mention_time,
                'score': crisis_score,
                'level': crisis_level
            })
            
            # Clean old detections
            self._clean_old_detections(brand, mention_time)
        
        # Calculate velocity
        velocity_score = self._calculate_velocity(brand, mention_time)
        
        # Adjust final score based on velocity
        final_score = min(crisis_score + velocity_score * 0.3, 1.0)
        final_level = self._determine_crisis_level(final_score)
        
        return {
            'crisis_score': round(final_score, 3),
            'crisis_level': final_level,
            'base_score': round(base_score, 3),
            'velocity_score': round(velocity_score, 3),
            'intensity_multiplier': round(intensity_multiplier, 2),
            'signals': {
                'keywords': keyword_signals,
                'sentiment': sentiment_signals,
                'patterns': pattern_signals
            },
            'detected_keywords': self._extract_matched_keywords(text_lower),
            'urgency': self._calculate_urgency(final_score, velocity_score),
            'timestamp': mention_time.isoformat() if mention_time else None
        }
    
    def _detect_keyword_signals(self, text: str) -> Dict:
        """Detect crisis keywords by severity"""
        signals = {'critical': 0, 'major': 0, 'moderate': 0}
        
        for severity, keywords in self.crisis_keywords.items():
            matches = sum(1 for keyword in keywords if keyword in text)
            signals[severity] = matches
        
        return signals
    
    def _detect_sentiment_signals(self, text: str) -> Dict:
        """Detect sentiment-based crisis signals"""
        # Simple sentiment indicators for crisis detection
        negative_indicators = [
            'hate', 'worst', 'terrible', 'awful', 'horrible', 'disgusting',
            'never again', 'boycott', 'avoid', 'warning', 'beware',
            'disappointed', 'furious', 'outraged', 'disgusted'
        ]
        
        text_lower = text.lower()
        negative_count = sum(1 for indicator in negative_indicators if indicator in text_lower)
        
        return {
            'negative_intensity': min(negative_count / 3.0, 1.0),
            'negative_keywords': negative_count
        }
    
    def _detect_pattern_signals(self, text: str) -> Dict:
        """Detect crisis patterns (caps, punctuation, etc.)"""
        signals = {}
        
        # All caps words (excluding common abbreviations)
        caps_words = re.findall(r'\b[A-Z]{3,}\b', text)
        caps_words = [w for w in caps_words if w not in ['USA', 'CEO', 'CFO', 'CTO', 'FAQ', 'API']]
        signals['caps_words'] = len(caps_words)
        
        # Excessive punctuation
        signals['exclamation_marks'] = len(re.findall(r'!+', text))
        signals['question_marks'] = len(re.findall(r'\?+', text))
        
        # Urgency patterns
        urgency_patterns = [
            r'\b(urgent|immediately|asap|emergency|critical|breaking)\b',
            r'\b(happening now|right now|just happened)\b'
        ]
        signals['urgency_indicators'] = sum(
            len(re.findall(pattern, text, re.IGNORECASE)) for pattern in urgency_patterns
        )
        
        return signals
    
    def _calculate_base_score(self, keyword_signals: Dict, sentiment_signals: Dict, pattern_signals: Dict) -> float:
        """Calculate base crisis score from all signals"""
        # Keyword score (weighted by severity)
        keyword_score = (
            keyword_signals['critical'] * 0.8 +
            keyword_signals['major'] * 0.5 +
            keyword_signals['moderate'] * 0.2
        )
        keyword_score = min(keyword_score / 3.0, 1.0)  # Normalize
        
        # Sentiment score
        sentiment_score = sentiment_signals['negative_intensity']
        
        # Pattern score
        pattern_score = min(
            (pattern_signals['caps_words'] * 0.2 +
             pattern_signals['exclamation_marks'] * 0.1 +
             pattern_signals['urgency_indicators'] * 0.3) / 2.0,
            1.0
        )
        
        # Weighted combination
        base_score = (
            keyword_score * 0.6 +
            sentiment_score * 0.3 +
            pattern_score * 0.1
        )
        
        return base_score
    
    def _calculate_intensity_multiplier(self, text: str) -> float:
        """Calculate intensity multiplier based on text patterns"""
        multiplier = 1.0
        
        for pattern, factor in self.intensity_patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                multiplier *= factor
        
        # Cap at reasonable maximum
        return min(multiplier, 2.0)
    
    def _determine_crisis_level(self, score: float) -> str:
        """Determine crisis level from score"""
        if score >= 0.8:
            return 'critical'
        elif score >= 0.6:
            return 'major'
        elif score >= 0.3:
            return 'moderate'
        elif score >= 0.1:
            return 'minor'
        else:
            return 'none'
    
    def _extract_matched_keywords(self, text: str) -> List[str]:
        """Extract crisis keywords found in text"""
        matched = []
        
        for severity, keywords in self.crisis_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    matched.append(keyword)
        
        return matched
    
    def _calculate_velocity(self, brand: str, current_time: datetime) -> float:
        """Calculate crisis velocity (rate of crisis mentions)"""
        if brand not in self.recent_detections:
            return 0.0
        
        recent = self.recent_detections[brand]
        
        # Count detections in velocity window
        window_start = current_time - self.velocity_window
        recent_count = sum(
            1 for detection in recent 
            if detection['timestamp'] >= window_start
        )
        
        # Calculate velocity score (0-1)
        # High velocity = many crisis mentions in short time
        velocity_score = min(recent_count / 10.0, 1.0)
        
        return velocity_score
    
    def _clean_old_detections(self, brand: str, current_time: datetime):
        """Remove old detections outside velocity window"""
        if brand not in self.recent_detections:
            return
        
        cutoff_time = current_time - self.velocity_window * 2  # Keep extra history
        
        self.recent_detections[brand] = [
            detection for detection in self.recent_detections[brand]
            if detection['timestamp'] >= cutoff_time
        ]
    
    def _calculate_urgency(self, crisis_score: float, velocity_score: float) -> str:
        """Calculate urgency level for response prioritization"""
        combined_score = crisis_score + velocity_score * 0.5
        
        if combined_score >= 0.8:
            return 'immediate'
        elif combined_score >= 0.6:
            return 'high'
        elif combined_score >= 0.4:
            return 'medium'
        elif combined_score >= 0.2:
            return 'low'
        else:
            return 'monitor'
    
    async def batch_detect_crisis(self, mentions: List[Dict], brand: str) -> List[Dict]:
        """Detect crisis in multiple mentions efficiently"""
        results = []
        
        for mention in mentions:
            text = mention.get('text', '')
            mention_time = mention.get('timestamp')
            
            if isinstance(mention_time, str):
                try:
                    mention_time = datetime.fromisoformat(mention_time.replace('Z', '+00:00'))
                except:
                    mention_time = datetime.now()
            elif mention_time is None:
                mention_time = datetime.now()
            
            result = await self.detect_crisis(text, brand, mention_time)
            results.append(result)
        
        return results
    
    def get_brand_crisis_summary(self, brand: str) -> Dict:
        """Get crisis summary for a brand"""
        if brand not in self.recent_detections:
            return {
                'total_incidents': 0,
                'recent_incidents': 0,
                'max_score': 0.0,
                'avg_score': 0.0,
                'current_velocity': 0.0,
                'risk_level': 'low'
            }
        
        recent = self.recent_detections[brand]
        now = datetime.now()
        
        # Recent incidents (last 24 hours)
        recent_window = now - timedelta(hours=24)
        recent_incidents = [
            d for d in recent 
            if d['timestamp'] >= recent_window
        ]
        
        scores = [d['score'] for d in recent_incidents]
        
        return {
            'total_incidents': len(recent),
            'recent_incidents': len(recent_incidents),
            'max_score': max(scores) if scores else 0.0,
            'avg_score': sum(scores) / len(scores) if scores else 0.0,
            'current_velocity': self._calculate_velocity(brand, now),
            'risk_level': self._assess_risk_level(scores, len(recent_incidents))
        }
    
    def _assess_risk_level(self, scores: List[float], incident_count: int) -> str:
        """Assess overall risk level for a brand"""
        if not scores:
            return 'low'
        
        max_score = max(scores)
        avg_score = sum(scores) / len(scores)
        
        if max_score >= 0.8 or (avg_score >= 0.5 and incident_count >= 5):
            return 'critical'
        elif max_score >= 0.6 or (avg_score >= 0.4 and incident_count >= 3):
            return 'high'
        elif max_score >= 0.4 or incident_count >= 2:
            return 'medium'
        else:
            return 'low'
