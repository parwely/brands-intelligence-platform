#!/usr/bin/env python3
"""
🚀 Brand Intelligence Platform - Simple ML Demo
============================================

Quick demonstration of working ML capabilities.
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_sentiment():
    """Test sentiment analysis endpoint"""
    print("🎯 Testing Sentiment Analysis")
    print("=" * 40)
    
    test_cases = [
        "I absolutely love this amazing product!",
        "This is terrible, worst experience ever.",
        "The product is okay, nothing special.",
        "URGENT: Safety issue detected!"
    ]
    
    for i, text in enumerate(test_cases, 1):
        print(f"\n📝 Test {i}: '{text[:40]}...'")
        
        # Test keyword-based analysis
        response = requests.post(f"{BASE_URL}/ml/analyze/sentiment", json={
            "text": text,
            "use_bert": False
        })
        
        if response.status_code == 200:
            data = response.json()['data']
            final = data['final_sentiment']
            print(f"   💭 Sentiment: {final['sentiment_label']} (confidence: {final['confidence']:.3f})")
            if final.get('crisis_indicators', 0) > 0:
                print(f"   🚨 Crisis Indicators: {final['crisis_indicators']}")
        else:
            print(f"   ❌ Error: {response.status_code}")

def test_features():
    """Test feature extraction"""
    print("\n🎯 Testing Feature Extraction")
    print("=" * 40)
    
    text = "This amazing product exceeded expectations! Highly recommended for everyone."
    
    response = requests.post(f"{BASE_URL}/ml/extract/features", json={
        "text": text
    })
    
    if response.status_code == 200:
        result = response.json()
        if 'data' in result:
            features = result['data']
        else:
            features = result  # Handle different response formats
            
        print(f"📝 Text: '{text}'")
        print(f"📏 Length: {features.get('length', 'N/A')}")
        print(f"📊 Word Count: {features.get('word_count', 'N/A')}")
        print(f"🔤 Character Count: {features.get('char_count', 'N/A')}")
        print(f"🚨 Has Crisis Keywords: {features.get('has_crisis_keywords', 'N/A')}")
    else:
        print(f"❌ Error: {response.status_code} - {response.text}")

def test_status():
    """Test ML service status"""
    print("🎯 ML Service Status")
    print("=" * 40)
    
    response = requests.get(f"{BASE_URL}/ml/status")
    if response.status_code == 200:
        status = response.json()
        print(f"✅ Status: {status.get('status', 'Unknown')}")
        data = status.get('data', {})
        print(f"📊 Components: {data.get('components', [])}")
        print(f"🤖 BERT Model: {data.get('bert_model', 'Not specified')}")
    else:
        print(f"❌ Error: {response.status_code}")

def main():
    print("🚀 Brand Intelligence Platform - ML Demo")
    print("=" * 50)
    
    try:
        test_status()
        test_sentiment()
        test_features()
        
        print(f"\n🌐 Interactive API Docs: {BASE_URL}/docs")
        print("✅ Core ML functionality demonstrated!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API server.")
        print("   Make sure the server is running: uvicorn app.main:app --reload")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
