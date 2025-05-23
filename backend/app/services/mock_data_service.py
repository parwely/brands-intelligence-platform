# backend/app/services/mock_data_service.py
import random
from datetime import datetime, timedelta
from typing import List, Dict
import uuid

class MockDataService:
    """
    Generiert realistische Demo-Daten ohne externe APIs
    Perfekt für Portfolio/Demo-Zwecke
    """
    
    # Realistische Brands für Demo
    DEMO_BRANDS = [
        {"name": "TechCorp", "industry": "Technology", "keywords": ["techcorp", "tech innovation", "AI solutions"]},
        {"name": "GreenEnergy", "industry": "Energy", "keywords": ["greenenergy", "solar", "sustainable"]},
        {"name": "FashionForward", "industry": "Fashion", "keywords": ["fashionforward", "style", "trendy"]},
        {"name": "HealthPlus", "industry": "Healthcare", "keywords": ["healthplus", "wellness", "medical"]},
    ]
    
    # Realistische Social Media Inhalte
    POSITIVE_TEMPLATES = [
        "Just tried {brand} - absolutely amazing! Highly recommend 👍 #satisfied",
        "Best decision ever choosing {brand}. Outstanding service! ⭐⭐⭐⭐⭐",
        "{brand} exceeded my expectations. Will definitely use again! 💯",
        "Wow! {brand} really knows how to treat customers. Impressed! 🔥",
        "Finally found a company that cares - {brand} is the real deal! ❤️"
    ]
    
    NEGATIVE_TEMPLATES = [
        "Disappointed with {brand} service. Expected much better... 😞",
        "{brand} needs to step up their game. Not happy with recent experience",
        "Having issues with {brand} - customer service not responding 😤",
        "Used to love {brand} but quality has declined recently 📉",
        "{brand} charged me twice! Still waiting for refund... #frustrated"
    ]
    
    NEUTRAL_TEMPLATES = [
        "Anyone else using {brand}? Looking for reviews before I try",
        "Saw an ad for {brand} - has anyone tried their new service?",
        "{brand} seems interesting but need more info before deciding",
        "Comparing {brand} with competitors. What's your experience?",
        "Thinking about switching to {brand} - pros and cons?"
    ]
    
    CRISIS_TEMPLATES = [
        "URGENT: {brand} data breach affects millions of users!! 🚨 #security",
        "BREAKING: {brand} CEO scandal - stock prices plummeting 📰",
        "Major outage at {brand} - services down for 12+ hours #outage",
        "ALERT: {brand} product recall due to safety concerns ⚠️",
        "Lawsuit filed against {brand} for misleading advertising #legal"
    ]
    
    PLATFORMS = ["twitter", "facebook", "reddit", "instagram", "news", "review_sites"]
    AUTHORS = ["@tech_enthusiast", "@consumer_watch", "@jane_doe", "@industry_insider", 
               "@daily_news", "@product_reviewer", "@social_butterfly", "@critical_thinker"]

    def generate_mentions(self, brand_name: str, days: int = 30, count: int = 100) -> List[Dict]:
        """Generiert realistische Mentions für eine Brand"""
        mentions = []
        
        for _ in range(count):
            mention = self._create_mention(brand_name, days)
            mentions.append(mention)
        
        return mentions
    
    def _create_mention(self, brand_name: str, days: int) -> Dict:
        """Erstellt eine einzelne realistische Mention"""
        
        # Zufällige Gewichtung für realistischere Verteilung
        sentiment_weights = [0.6, 0.3, 0.08, 0.02]  # positive, neutral, negative, crisis
        sentiment_type = random.choices(
            ["positive", "neutral", "negative", "crisis"], 
            weights=sentiment_weights
        )[0]
        
        # Template basierend auf Sentiment auswählen
        template_map = {
            "positive": self.POSITIVE_TEMPLATES,
            "neutral": self.NEUTRAL_TEMPLATES, 
            "negative": self.NEGATIVE_TEMPLATES,
            "crisis": self.CRISIS_TEMPLATES
        }
        
        # Sentiment Score generieren
        sentiment_ranges = {
            "positive": (0.3, 1.0),
            "neutral": (-0.2, 0.2),
            "negative": (-0.8, -0.3),
            "crisis": (-1.0, -0.7)
        }
        
        # Crisis Probability
        crisis_probs = {
            "positive": (0.0, 0.1),
            "neutral": (0.0, 0.2),
            "negative": (0.2, 0.6),
            "crisis": (0.8, 1.0)
        }
        
        sentiment_range = sentiment_ranges[sentiment_type]
        crisis_range = crisis_probs[sentiment_type]
        
        # Zufällige Zeitpunkt in den letzten X Tagen
        random_date = datetime.utcnow() - timedelta(
            days=random.randint(0, days),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59)
        )
        
        return {
            "id": str(uuid.uuid4()),
            "platform": random.choice(self.PLATFORMS),
            "content": random.choice(template_map[sentiment_type]).format(brand=brand_name),
            "author": random.choice(self.AUTHORS),
            "url": f"https://demo-platform.com/posts/{random.randint(100000, 999999)}",
            "sentiment_score": round(random.uniform(*sentiment_range), 3),
            "crisis_probability": round(random.uniform(*crisis_range), 3),
            "influence_score": round(random.uniform(0.1, 1.0), 3),
            "published_at": random_date,
            "created_at": datetime.utcnow(),
            "processed_at": datetime.utcnow()
        }
    
    def generate_trend_data(self, days: int = 30) -> List[Dict]:
        """Generiert Trend-Daten für Charts"""
        trend_data = []
        
        for i in range(days):
            date = datetime.utcnow() - timedelta(days=days-i)
            
            # Simuliere realistische Trends mit etwas Volatilität
            base_sentiment = 0.3 + 0.4 * random.random()  # Basis positiv
            daily_volatility = random.uniform(-0.2, 0.2)
            sentiment = max(-1, min(1, base_sentiment + daily_volatility))
            
            trend_data.append({
                "date": date.date().isoformat(),
                "sentiment": round(sentiment, 3),
                "mention_count": random.randint(10, 150),
                "crisis_score": round(random.uniform(0.0, 0.3), 3)
            })
        
        return trend_data
    
    def generate_competitive_analysis(self) -> Dict:
        """Generiert Competitive Intelligence Daten"""
        competitors = ["CompetitorA", "CompetitorB", "CompetitorC", "CompetitorD"]
        
        analysis = {
            "market_share": {},
            "sentiment_comparison": {},
            "mention_volume": {}
        }
        
        total_share = 100
        for competitor in competitors:
            share = random.randint(10, 30)
            total_share -= share
            analysis["market_share"][competitor] = share
            analysis["sentiment_comparison"][competitor] = round(random.uniform(-0.5, 0.8), 3)
            analysis["mention_volume"][competitor] = random.randint(500, 5000)
        
        # Rest für "Others"
        analysis["market_share"]["Others"] = max(0, total_share)
        
        return analysis

# Singleton instance
mock_service = MockDataService()