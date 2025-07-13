#!/usr/bin/env python3
# Direct test of ML components without FastAPI import issues
import sys
import asyncio
sys.path.append('.')

# Test direct imports
def test_direct_imports():
    print("🔧 Testing direct ML component imports...")
    
    try:
        from app.ml.sentiment.analyzer import SentimentAnalyzer
        print("✅ SentimentAnalyzer imported")
        
        from app.ml.sentiment.bert_analyzer import BERTSentimentAnalyzer  
        print("✅ BERTSentimentAnalyzer imported")
        
        from app.ml.sentiment.crisis_detector import CrisisDetector
        print("✅ CrisisDetector imported")
        
        print("✅ All ML components available!")
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

async def test_ml_functionality():
    print("\n🚀 Testing ML Service Functionality")
    print("=" * 50)
    
    try:
        # Import and initialize each component separately
        from app.ml.sentiment.analyzer import SentimentAnalyzer
        from app.ml.sentiment.bert_analyzer import BERTSentimentAnalyzer
        from app.ml.sentiment.crisis_detector import CrisisDetector
        
        # Test Sentiment Analysis
        print("\n💭 Testing Sentiment Analysis...")
        analyzer = SentimentAnalyzer()
        test_text = "I absolutely love this amazing product! It works perfectly."
        sentiment = await analyzer.analyze_best_available(test_text)
        print(f"   Text: '{test_text}'")
        print(f"   Result: {sentiment.get('sentiment_label')} (score: {sentiment.get('sentiment_score', 0):.3f})")
        
        # Test BERT Analysis
        print("\n🤖 Testing BERT Analysis...")
        bert_analyzer = BERTSentimentAnalyzer()
        if bert_analyzer.available:
            bert_result = await bert_analyzer.analyze_sentiment(test_text)
            print(f"   BERT Result: {bert_result.get('sentiment_label')} (score: {bert_result.get('sentiment_score', 0):.3f})")
        else:
            print("   BERT not available, using fallback")
        
        # Test Crisis Detection
        print("\n🚨 Testing Crisis Detection...")
        crisis_detector = CrisisDetector()
        
        crisis_mentions = [
            {
                'text': 'This product is absolutely terrible and dangerous! Major safety issues!',
                'timestamp': '2024-01-01T12:00:00'
            },
            {
                'text': 'Lawsuit filed against company for fraud and corruption!',
                'timestamp': '2024-01-01T12:01:00'
            }
        ]
        
        crisis_results = await crisis_detector.batch_detect_crisis(crisis_mentions, 'TestBrand')
        for i, result in enumerate(crisis_results):
            print(f"   Mention {i+1}: {result.get('crisis_level')} (score: {result.get('crisis_score', 0):.3f})")
        
        # Summary
        print(f"\n🎉 ML Pipeline Test Complete!")
        print(f"✅ Sentiment Analysis: Working")
        print(f"✅ BERT Integration: {'Available' if bert_analyzer.available else 'Fallback Mode'}")
        print(f"✅ Crisis Detection: Working")
        
        return True
        
    except Exception as e:
        print(f"❌ ML test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def demonstrate_api_endpoints():
    print(f"\n📡 ML API Endpoints Available:")
    print(f"=" * 50)
    
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
    
    for endpoint in endpoints:
        print(f"   {endpoint}")
    
    print(f"\n🌐 Example API Usage:")
    print(f"""
    # Analyze sentiment
    curl -X POST "http://localhost:8000/ml/analyze/sentiment" \\
         -H "Content-Type: application/json" \\
         -d '{{"text": "I love this product!", "use_bert": true}}'
    
    # Demo analysis  
    curl "http://localhost:8000/ml/test/demo"
    
    # Get ML service status
    curl "http://localhost:8000/ml/status"
    """)

def main():
    print("🚀 Brand Intelligence Platform - ML Pipeline Demo")
    print("=" * 60)
    
    # Test imports
    if not test_direct_imports():
        return
    
    # Test functionality
    success = asyncio.run(test_ml_functionality())
    
    if success:
        # Show API info
        asyncio.run(demonstrate_api_endpoints())
        
        print(f"\n🎯 Phase 3 Complete: Real-time ML Pipeline Integration!")
        print(f"🔧 Next Steps:")
        print(f"   1. Start the API: uvicorn app.main:app --reload")
        print(f"   2. Test endpoints: http://localhost:8000/ml/test/demo") 
        print(f"   3. View API docs: http://localhost:8000/docs")
        print(f"   4. Integrate with frontend dashboard")
    else:
        print(f"\n🔧 Fix ML issues before proceeding")

if __name__ == "__main__":
    main()
