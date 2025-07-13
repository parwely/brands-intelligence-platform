#!/usr/bin/env python3
# Test script for ML Service functionality
import sys
import asyncio
sys.path.append('.')

async def test_ml_service():
    print("🚀 Testing Brand Intelligence ML Service")
    print("=" * 50)
    
    try:
        # Import ML Service
        from app.services.ml_service import MLService
        print("✅ MLService imported successfully")
        
        # Initialize ML Service
        ml_service = MLService()
        print("✅ MLService initialized")
        
        # Test service status
        status = ml_service.get_service_status()
        print(f"📊 Service Status: {status}")
        
        # Test sentiment analysis
        test_text = "I absolutely love this amazing product! It works perfectly."
        print(f"\n🧪 Testing sentiment analysis with: '{test_text}'")
        
        sentiment_result = await ml_service.analyze_mention_sentiment(test_text)
        final_sentiment = sentiment_result.get('final_sentiment', {})
        print(f"💭 Sentiment: {final_sentiment.get('sentiment_label', 'unknown')} "
              f"(score: {final_sentiment.get('sentiment_score', 0):.3f})")
        
        # Test crisis detection
        print(f"\n🚨 Testing crisis detection...")
        test_mentions = [
            {
                'text': 'This product is absolutely terrible and dangerous! Avoid at all costs!',
                'timestamp': '2024-01-01T12:00:00',
                'id': 'mention_1'
            },
            {
                'text': 'I love this brand, great quality!',
                'timestamp': '2024-01-01T12:01:00', 
                'id': 'mention_2'
            },
            {
                'text': 'Major lawsuit filed against company for fraud and corruption!',
                'timestamp': '2024-01-01T12:02:00',
                'id': 'mention_3'
            }
        ]
        
        crisis_result = await ml_service.analyze_crisis(test_mentions, 'TestBrand')
        print(f"⚠️  Crisis Level: {crisis_result.get('overall_crisis_level', 'none')} "
              f"(score: {crisis_result.get('max_crisis_score', 0):.3f})")
        
        # Test brand health analysis
        print(f"\n🏥 Testing brand health analysis...")
        health_result = await ml_service.analyze_brand_health('TestBrand', test_mentions)
        health_score = health_result.get('health_score', 0)
        health_level = health_result.get('health_level', 'unknown')
        print(f"💚 Brand Health: {health_level} ({health_score}/100)")
        
        # Show recommendations
        recommendations = health_result.get('recommendations', [])
        if recommendations:
            print(f"\n📋 Recommendations:")
            for i, rec in enumerate(recommendations[:3], 1):
                print(f"   {i}. {rec}")
        
        print(f"\n🎉 All ML components working successfully!")
        print(f"🔧 Available components:")
        print(f"   • Sentiment Analyzer: {'✅' if status.get('sentiment_analyzer') else '❌'}")
        print(f"   • BERT Analyzer: {'✅' if status.get('bert_analyzer') else '❌'}")
        print(f"   • Crisis Detector: {'✅' if status.get('crisis_detector') else '❌'}")
        print(f"   • Text Preprocessor: {'✅' if status.get('text_preprocessor') else '❌'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_ml_service())
    if success:
        print(f"\n🎯 Ready to continue with Phase 3: Real-time ML Pipeline Integration!")
    else:
        print(f"\n🔧 Need to fix ML service issues before proceeding.")
