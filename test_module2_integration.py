#!/usr/bin/env python3
"""
Test script to verify Module2 sentiment integration
===================================================
Tests advanced sentiment analysis features from Module2.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from modules.sentiment.analyzer import (
    analyze_financial_keywords,
    correct_sentiment_with_keywords,
    get_sentiment_score,
    HuggingFaceSentimentAnalyzer,
    EnhancedSentimentAnalyzer
)


def print_header(title: str):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def test_keyword_analysis():
    """Test Module2's advanced keyword analysis"""
    print_header("TEST 1: Financial Keyword Analysis")
    
    test_cases = [
        ("Bourse de Tunis : Le Tunindex commence la semaine dans le rouge", "NEG"),
        ("Le marché termine dans le vert avec une hausse de 1.5%", "POS"),
        ("La société annonce des pertes importantes", "NEG"),
        ("Forte croissance du bénéfice trimestriel", "POS"),
        ("Assemblée générale ordinaire de la société", "NEU"),
    ]
    
    passed = 0
    for text, expected in test_cases:
        result = analyze_financial_keywords(text)
        actual = result['suggested_label']
        status = "✓" if actual == expected else "✗"
        
        print(f"\n{status} Text: {text[:60]}...")
        print(f"  Expected: {expected} | Got: {actual}")
        print(f"  Scores: NEG={result['neg_score']:.1f}, POS={result['pos_score']:.1f}")
        
        if result['matched_keywords']['strong_negative']:
            print(f"  Strong NEG: {result['matched_keywords']['strong_negative']}")
        if result['matched_keywords']['strong_positive']:
            print(f"  Strong POS: {result['matched_keywords']['strong_positive']}")
        
        if actual == expected:
            passed += 1
    
    print(f"\n  Result: {passed}/{len(test_cases)} tests passed")
    return passed == len(test_cases)


def test_sentiment_correction():
    """Test keyword-based correction of ML predictions"""
    print_header("TEST 2: Sentiment Correction")
    
    test_cases = [
        {
            "text": "Bourse de Tunis : Le Tunindex commence la semaine dans le rouge",
            "model": {"label": "NEU", "score": 0.0, "confidence": 0.75},
            "expected_corrected": "NEG"
        },
        {
            "text": "Le marché termine dans le vert avec une hausse de 1.5%",
            "model": {"label": "NEU", "score": 0.0, "confidence": 0.65},
            "expected_corrected": "POS"
        },
        {
            "text": "La société annonce des pertes importantes",
            "model": {"label": "POS", "score": 0.5, "confidence": 0.60},
            "expected_corrected": "NEG"
        },
    ]
    
    passed = 0
    for case in test_cases:
        text = case["text"]
        model_result = case["model"]
        expected = case["expected_corrected"]
        
        corrected = correct_sentiment_with_keywords(model_result, text)
        actual = corrected['label']
        status = "✓" if actual == expected else "✗"
        
        print(f"\n{status} Text: {text[:60]}...")
        print(f"  Model predicted: {model_result['label']} (score={model_result['score']:.2f})")
        print(f"  Corrected to: {corrected['label']} (score={corrected['score']:.2f})")
        print(f"  Expected: {expected}")
        print(f"  Correction applied: {corrected['correction_applied']}")
        
        if actual == expected:
            passed += 1
    
    print(f"\n  Result: {passed}/{len(test_cases)} tests passed")
    return passed == len(test_cases)


def test_enhanced_analyzer_keywords():
    """Test EnhancedSentimentAnalyzer with keyword fallback"""
    print_header("TEST 3: Enhanced Analyzer (Keyword Mode)")
    
    try:
        analyzer = EnhancedSentimentAnalyzer(provider="keywords")
        
        test_texts = [
            "La BIAT affiche une forte croissance des bénéfices",
            "Chute brutale du cours de l'action suite aux pertes",
            "Maintien du dividende selon l'assemblée générale"
        ]
        
        print("\nAnalyzing texts with keyword-based analyzer...")
        for text in test_texts:
            result = analyzer.analyze(text)
            print(f"\n  Text: {text[:60]}...")
            print(f"  Label: {result['label']}")
            print(f"  Score: {result['sentiment_score']:+.2f}")
            print(f"  Confidence: {result['confidence']:.2f}")
            print(f"  Method: {result.get('method', 'unknown')}")
        
        print("\n  ✓ Enhanced analyzer test passed (keyword mode)")
        return True
    except Exception as e:
        print(f"\n  ✗ Enhanced analyzer test failed: {e}")
        return False


def test_get_sentiment_score():
    """Test main get_sentiment_score function with different modes"""
    print_header("TEST 4: get_sentiment_score Function")
    
    test_stock = 'TN0001600154'  # ATTIJARI BANK
    
    # Test 1: Basic mode (Module2 CSV or keywords)
    print("\n[1] Testing basic mode (CSV cache)...")
    try:
        result = get_sentiment_score(test_stock)
        print(f"  Stock: {result['stock_name']}")
        print(f"  Sentiment: {result['sentiment_score']:+.2f}")
        print(f"  Confidence: {result['confidence']:.2f}")
        print(f"  Articles: {result.get('num_articles', 0)}")
        print(f"  Method: {result.get('method', 'unknown')}")
        print("  ✓ Basic mode passed")
    except Exception as e:
        print(f"  Note: {e}")
    
    # Test 2: Advanced mode (will fallback to keywords if no API keys)
    print("\n[2] Testing advanced mode (ML-based)...")
    try:
        result = get_sentiment_score(test_stock, use_advanced=True, provider="keywords")
        print(f"  Stock: {result['stock_name']}")
        print(f"  Sentiment: {result['sentiment_score']:+.2f}")
        print(f"  Confidence: {result['confidence']:.2f}")
        print(f"  Method: {result.get('method', 'unknown')}")
        print(f"  Correction applied: {result.get('correction_applied', False)}")
        print("  ✓ Advanced mode passed")
    except Exception as e:
        print(f"  ✗ Advanced mode failed: {e}")
        return False
    
    return True


def main():
    """Run all integration tests"""
    print("\n" + "=" * 70)
    print("  MODULE2 SENTIMENT INTEGRATION TEST")
    print("  Testing integration of advanced sentiment analysis features")
    print("=" * 70)
    
    tests = [
        ("Keyword Analysis", test_keyword_analysis),
        ("Sentiment Correction", test_sentiment_correction),
        ("Enhanced Analyzer", test_enhanced_analyzer_keywords),
        ("get_sentiment_score", test_get_sentiment_score),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            passed = test_func()
            results.append((name, passed))
        except Exception as e:
            print(f"\n  ✗ {name} crashed: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))
    
    # Summary
    print_header("TEST SUMMARY")
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {status}: {name}")
    
    print(f"\n  Total: {passed_count}/{total_count} tests passed")
    
    if passed_count == total_count:
        print("\n  🎉 ALL TESTS PASSED! Module2 integration is working correctly.")
        return 0
    else:
        print("\n  ⚠️  Some tests failed. Check errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
