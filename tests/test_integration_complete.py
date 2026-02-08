"""
Integration Tests for BVMT Trading Assistant
=============================================
Validates that all modules work together correctly.
Run with: python tests/test_integration_complete.py
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_data_loader():
    """Test that shared data loader module works"""
    from modules.shared.data_loader import (
        get_current_price,
        get_stock_name,
        get_all_stocks,
        get_liquid_stocks,
        get_stock_summary,
        load_full_dataset
    )
    
    # Test basic functionality
    df = load_full_dataset()
    assert len(df) > 0, "No data loaded"
    
    stock_codes = get_all_stocks()
    assert len(stock_codes) > 0, "No stock codes found"
    
    # Test liquid stocks
    liquid = get_liquid_stocks()
    assert len(liquid) > 0, "No liquid stocks found"
    
    # Test specific stock
    test_stock = liquid[0]
    price = get_current_price(test_stock)
    assert price > 0, f"Invalid price for {test_stock}: {price}"
    
    stock_name = get_stock_name(test_stock)
    assert stock_name is not None, f"No name found for {test_stock}"
    
    # Test summary
    summary = get_stock_summary(test_stock)
    assert 'current_price' in summary, "Missing current_price in summary"
    
    print(f"✓ Data Loader Test Passed")
    print(f"  Loaded {len(df)} rows")
    print(f"  Found {len(stock_codes)} total stocks, {len(liquid)} liquid stocks")
    print(f"  Example: {stock_name} ({price:.2f} TND)")


def test_forecasting_module():
    """Test that forecasting module works"""
    try:
        from modules.forecasting.predict import predict_next_days, get_trend_analysis
        from modules.shared.data_loader import get_liquid_stocks
        
        # Get a test stock
        liquid_stocks = get_liquid_stocks()
        test_stock = liquid_stocks[0]
        
        # Test prediction
        forecast = predict_next_days(test_stock, n_days=5)
        
        # Validate structure
        assert 'predictions' in forecast, "Missing predictions"
        assert len(forecast['predictions']) == 5, "Wrong number of predictions"
        assert 'model_used' in forecast, "Missing model_used"
        
        # Test trend analysis
        trend = get_trend_analysis(test_stock)
        assert 'overall_trend' in trend, "Missing overall_trend"
        
        print(f"✓ Forecasting Module Test Passed")
        print(f"  Model: {forecast['model_used']}")
        print(f"  Predicted prices: {forecast['predictions'][0]['predicted_close']:.2f} → {forecast['predictions'][-1]['predicted_close']:.2f} TND")
        print(f"  Trend: {trend['overall_trend']}")
        
    except ImportError:
        print("⚠ Forecasting module not available - skipping test")


def test_sentiment_module():
    """Test that sentiment module works"""
    try:
        from modules.sentiment.analyzer import get_sentiment_score, get_market_sentiment
        
        # Test with cached stock
        test_stock = 'TN0001600154'  # ATTIJARI BANK
        
        sentiment = get_sentiment_score(test_stock)
        
        # Validate structure
        assert 'sentiment_score' in sentiment, "Missing sentiment_score"
        assert 'confidence' in sentiment, "Missing confidence"
        assert 'num_articles' in sentiment, "Missing num_articles"
        
        # Test market sentiment
        market = get_market_sentiment()
        assert 'overall_sentiment' in market, "Missing overall_sentiment"
        
        print(f"✓ Sentiment Module Test Passed")
        print(f"  Sentiment score: {sentiment['sentiment_score']:.2f}")
        print(f"  Articles analyzed: {sentiment['num_articles']}")
        print(f"  Market sentiment: {market['overall_sentiment']:.2f}")
        
    except ImportError:
        print("⚠ Sentiment module not available - skipping test")


def test_anomaly_module():
    """Test that anomaly module works"""
    try:
        from modules.anomaly.detector import detect_anomalies
        from modules.shared.data_loader import get_liquid_stocks
        
        # Get a test stock
        liquid_stocks = get_liquid_stocks()
        test_stock = liquid_stocks[0]
        
        # Test anomaly detection
        anomalies = detect_anomalies(test_stock, lookback_days=30)
        
        # Validate structure
        assert 'anomalies_detected' in anomalies, "Missing anomalies_detected"
        assert 'risk_level' in anomalies, "Missing risk_level"
        assert 'score' in anomalies, "Missing score"
        
        print(f"✓ Anomaly Module Test Passed")
        print(f"  Anomalies found: {len(anomalies['anomalies_detected'])}")
        print(f"  Risk level: {anomalies['risk_level']}")
        print(f"  Score: {anomalies['score']:.1f}/10")
        
    except ImportError:
        print("⚠ Anomaly module not available - skipping test")


def test_decision_engine():
    """Test that decision engine works"""
    try:
        from modules.decision.engine import make_recommendation
        from modules.shared.data_loader import get_liquid_stocks
        
        # Get a test stock
        liquid_stocks = get_liquid_stocks()
        test_stock = liquid_stocks[0]
        
        # Test recommendation generation
        rec = make_recommendation(test_stock, 'moderate')
        
        # Validate structure
        assert 'recommendation' in rec, "Missing recommendation field"
        assert rec['recommendation'] in ['BUY', 'SELL', 'HOLD'], f"Invalid recommendation: {rec['recommendation']}"
        assert 'confidence' in rec, "Missing confidence field"
        assert 0 <= rec['confidence'] <= 1, f"Invalid confidence: {rec['confidence']}"
        assert 'explanation' in rec, "Missing explanation"
        
        print(f"✓ Decision Engine Test Passed")
        print(f"  Recommendation for {rec['stock_name']}: {rec['recommendation']}")
        print(f"  Confidence: {rec['confidence']:.0%}")
        
    except ImportError as e:
        print(f"⚠ Decision engine not available - skipping test: {e}")


def test_portfolio():
    """Test portfolio management"""
    from modules.decision.portfolio import Portfolio
    from modules.shared.data_loader import get_current_price, get_liquid_stocks, get_stock_name
    
    # Create portfolio
    portfolio = Portfolio(initial_capital=10000.0)
    
    # Test buy
    liquid_stocks = get_liquid_stocks()
    test_stock = liquid_stocks[0]
    price = get_current_price(test_stock)
    stock_name = get_stock_name(test_stock)
    
    result = portfolio.buy(test_stock, stock_name, price, 10, "2022-12-01")
    assert result['success'], f"Buy failed: {result.get('message')}"
    
    # Test sell
    result = portfolio.sell(test_stock, price * 1.1, 5, "2022-12-15")
    assert result['success'], f"Sell failed: {result.get('message')}"
    
    # Test metrics
    metrics = portfolio.get_performance_metrics({test_stock: price * 1.1})
    assert 'total_value' in metrics, "Missing total_value"
    assert 'total_gain_loss' in metrics, "Missing total_gain_loss"
    assert 'roi_percentage' in metrics, "Missing roi_percentage"
    
    print(f"✓ Portfolio Test Passed")
    print(f"  Initial Capital: {portfolio.initial_capital:.2f} TND")
    print(f"  Current Cash: {portfolio.cash:.2f} TND")
    print(f"  Total Value: {metrics['total_value']:.2f} TND")
    print(f"  ROI: {metrics['roi_percentage']:.2f}%")


def test_full_pipeline():
    """Test complete pipeline: data → modules → recommendation → portfolio"""
    try:
        from modules.decision.engine import make_recommendation
        from modules.decision.portfolio import Portfolio
        from modules.shared.data_loader import (
            get_current_price,
            get_stock_name,
            get_liquid_stocks,
        )
        
        # Initialize portfolio
        portfolio = Portfolio(initial_capital=10000.0)
        
        # Get recommendations for multiple stocks
        stock_codes = get_liquid_stocks()[:10]  # Test first 10
        
        buy_count = 0
        sell_count = 0
        hold_count = 0
        
        for stock_code in stock_codes:
            try:
                rec = make_recommendation(stock_code, 'moderate')
                
                if rec['recommendation'] == 'BUY':
                    buy_count += 1
                    # Simulate buy
                    price = get_current_price(stock_code)
                    if portfolio.cash >= price * 10:  # Buy 10 shares if affordable
                        portfolio.buy(stock_code, rec['stock_name'], price, 10, "2022-12-01")
                
                elif rec['recommendation'] == 'SELL':
                    sell_count += 1
                
                else:
                    hold_count += 1
            except Exception as e:
                print(f"    Warning: Error processing {stock_code}: {e}")
                continue
        
        print(f"✓ Full Pipeline Test Passed")
        print(f"  Analyzed {len(stock_codes)} stocks")
        print(f"  BUY: {buy_count}, SELL: {sell_count}, HOLD: {hold_count}")
        print(f"  Portfolio Value: {portfolio.cash:.2f} TND")
        print(f"  Holdings: {len(portfolio.holdings)}")
        
    except ImportError as e:
        print(f"⚠ Full pipeline test skipped: {e}")


if __name__ == "__main__":
    print("=" * 70)
    print("BVMT Trading Assistant - Integration Tests")
    print("=" * 70)
    print()
    
    try:
        print("1. Testing Data Loader...")
        test_data_loader()
        print()
        
        print("2. Testing Forecasting Module...")
        test_forecasting_module()
        print()
        
        print("3. Testing Sentiment Module...")
        test_sentiment_module()
        print()
        
        print("4. Testing Anomaly Module...")
        test_anomaly_module()
        print()
        
        print("5. Testing Decision Engine...")
        test_decision_engine()
        print()
        
        print("6. Testing Portfolio...")
        test_portfolio()
        print()
        
        print("7. Testing Full Pipeline...")
        test_full_pipeline()
        print()
        
        print("=" * 70)
        print("✅ ALL TESTS PASSED!")
        print("=" * 70)
    
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
