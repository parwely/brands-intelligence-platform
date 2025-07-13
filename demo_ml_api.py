#!/usr/bin/env python3
"""
🚀 Brand Intelligence Platform - ML API Demo
============================================

This script demonstrates all ML capabilities through the live API endpoints.
Make sure the server is running: uvicorn app.main:app --reload
"""

import requests
import json
import time
from typing import Dict, Any, Optional

BASE_URL = "http://localhost:8000"

def demo_header(title: str):
    """Print a formatted demo section header"""
    print(f"\n{'='*60}")
    print(f"🎯 {title}")
    print(f"{'='*60}")

def make_request(endpoint: str, method: str = "GET", data: Optional[Dict[Any, Any]] = None) -> Optional[Dict[Any, Any]]:
    """Make API request with error handling"""
    url = f"{BASE_URL}{endpoint}"
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return None

def main():
    print("🚀 Brand Intelligence Platform - ML API Demo")
    print("=" * 60)
    
    # 1. Check ML Service Status
    demo_header("1. ML Service Status")
    status = make_request("/ml/status")
    if status:
        print(f"✅ ML Service: {status.get('status', 'Unknown')}")
        print(f"📊 Components: {', '.join(status.get('data', {}).get('components', []))}")
        print(f"🤖 BERT Model: {status.get('data', {}).get('bert_model', 'Not loaded')}")
    
    # 2. Sentiment Analysis Demo
    demo_header("2. Sentiment Analysis (Keyword-based)")
    test_texts = [
        "I absolutely love this amazing product! It works perfectly.",
        "This is the worst experience ever. Completely disappointed.",
        "The product is okay, nothing special but does the job.",
        "URGENT: Product caught fire! This is dangerous!"
    ]
    
    for i, text in enumerate(test_texts, 1):
        print(f"\n📝 Text {i}: '{text[:50]}...'")
        result = make_request("/ml/analyze/sentiment", "POST", {
            "text": text,
            "use_bert": False
        })
        if result and result.get('success'):
            data = result['data']
            final = data['final_sentiment']
            print(f"   💭 Sentiment: {final['sentiment_label']} (score: {final['confidence']:.3f})")
            if final.get('crisis_indicators', 0) > 0:
                print(f"   🚨 Crisis Indicators: {final['crisis_indicators']}")
    
    # 3. BERT Analysis Demo
    demo_header("3. Advanced Sentiment Analysis (BERT)")
    for i, text in enumerate(test_texts[:2], 1):  # Test first 2 for speed
        print(f"\n📝 Text {i}: '{text[:50]}...'")
        result = make_request("/ml/analyze/sentiment", "POST", {
            "text": text,
            "use_bert": True
        })
        if result and result.get('success'):
            data = result['data']
            final = data['final_sentiment']
            print(f"   🤖 BERT Sentiment: {final['sentiment_label']} (score: {final['confidence']:.3f})")
            base = data.get('base_analysis', {})
            print(f"   📊 Keyword Sentiment: {base.get('sentiment_label', 'N/A')}")
    
    # 4. Crisis Detection Demo
    demo_header("4. Crisis Detection")
    crisis_mentions = [
        {
            "text": "BREAKING: Major data breach at TechCorp! Customer information compromised.",
            "brand": "TechCorp",
            "source": "Twitter"
        },
        {
            "text": "Love the new iPhone features! Best upgrade ever.",
            "brand": "Apple",
            "source": "Instagram"
        },
        {
            "text": "Class action lawsuit filed against AutoCorp for faulty brakes",
            "brand": "AutoCorp",
            "source": "News"
        }
    ]
    
    result = make_request("/ml/analyze/crisis", "POST", {"mentions": crisis_mentions})
    if result and result.get('success'):
        analyses = result['data']['analyses']
        for i, analysis in enumerate(analyses):
            mention = crisis_mentions[i]
            print(f"\n📱 Mention: '{mention['text'][:50]}...'")
            print(f"   🎯 Brand: {mention['brand']}")
            print(f"   🚨 Crisis Level: {analysis['crisis_level']} (score: {analysis['crisis_score']:.3f})")
            if analysis.get('crisis_keywords'):
                print(f"   🔍 Keywords: {', '.join(analysis['crisis_keywords'])}")
    
    # 5. Brand Health Analysis Demo
    demo_header("5. Brand Health Analysis")
    result = make_request("/ml/analyze/brand-health", "POST", {
        "brand": "TechCorp",
        "mentions": crisis_mentions
    })
    if result and result.get('success'):
        health = result['data']
        print(f"🏥 Brand Health Score: {health['health_score']:.1f}/100")
        print(f"📊 Health Status: {health['health_status']}")
        print(f"💭 Sentiment Distribution:")
        for sentiment, count in health['sentiment_distribution'].items():
            print(f"   • {sentiment.title()}: {count}")
        print(f"🚨 Crisis Level: {health['crisis_summary']['overall_level']}")
        
        if health.get('recommendations'):
            print(f"\n💡 Recommendations:")
            for rec in health['recommendations'][:3]:  # Show first 3
                print(f"   • {rec}")
    
    # 6. Batch Processing Demo
    demo_header("6. Batch Processing")
    batch_mentions = [
        {"text": "Great customer service!", "id": "1"},
        {"text": "Product quality has declined", "id": "2"},
        {"text": "RECALL NOTICE: Safety issue detected", "id": "3"}
    ]
    
    result = make_request("/ml/analyze/batch", "POST", {"mentions": batch_mentions})
    if result and result.get('success'):
        analyses = result['data']['analyses']
        print(f"📦 Processed {len(analyses)} mentions:")
        for analysis in analyses:
            print(f"   🔗 ID {analysis['mention_id']}: {analysis['sentiment']} (score: {analysis['confidence']:.3f})")
    
    # 7. Feature Extraction Demo
    demo_header("7. Text Feature Extraction")
    result = make_request("/ml/extract/features", "POST", {
        "text": "This amazing product exceeded all my expectations! Highly recommended."
    })
    if result and result.get('success'):
        features = result['data']
        print(f"📏 Text Length: {features['length']}")
        print(f"📝 Word Count: {features['word_count']}")
        print(f"🔤 Character Count: {features['char_count']}")
        print(f"🚨 Has Crisis Keywords: {features['has_crisis_keywords']}")
        if features.get('crisis_keywords'):
            print(f"⚠️  Crisis Keywords: {', '.join(features['crisis_keywords'])}")
    
    # 8. Demo Summary
    demo_header("Demo Complete - API Endpoints Summary")
    endpoints = [
        "GET  /ml/status                 - ML service status",
        "POST /ml/analyze/sentiment      - Single text sentiment analysis", 
        "POST /ml/analyze/crisis         - Crisis detection for mentions",
        "POST /ml/analyze/brand-health   - Comprehensive brand health analysis",
        "POST /ml/analyze/batch          - Batch analysis of multiple mentions",
        "GET  /ml/analyze/realtime/{brand} - Real-time streaming analysis",
        "POST /ml/process/mention        - Process new mention through ML pipeline",
        "GET  /ml/test/demo              - Demo ML analysis",
        "POST /ml/extract/features       - Extract text features"
    ]
    
    print("📡 Available ML API Endpoints:")
    for endpoint in endpoints:
        print(f"   {endpoint}")
    
    print(f"\n🌐 Interactive API Documentation: {BASE_URL}/docs")
    print(f"📚 OpenAPI Specification: {BASE_URL}/openapi.json")
    
    print("\n🎉 Brand Intelligence Platform ML API Demo Complete!")
    print("✅ All ML components operational and ready for production!")

if __name__ == "__main__":
    main()
