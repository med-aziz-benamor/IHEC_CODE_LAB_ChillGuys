"""
Integration Tests for Decision Engine
======================================
Run this to verify your module works before integrating with teammates.

Usage:
    python -m tests.test_integration

Or:
    python tests/test_integration.py
"""

import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.decision.engine import (
    make_recommendation,
    get_top_recommendations,
    get_market_summary,
    analyze_portfolio_stocks
)
from modules.decision.portfolio import Portfolio
from modules.decision.explainer import generate_explanation, generate_short_explanation
from modules.decision.mocks import get_all_stock_codes_mock


def test_recommendation_engine():
    """Test that we can generate recommendations"""
    print("\n" + "=" * 60)
    print("TEST 1: Recommendation Engine")
    print("=" * 60)

    # Test for a known stock
    result = make_recommendation('TN0001600154', user_profile='moderate')

    assert result['recommendation'] in ['BUY', 'SELL', 'HOLD'], \
        f"Invalid recommendation: {result['recommendation']}"
    assert 0 <= result['confidence'] <= 1, \
        f"Invalid confidence: {result['confidence']}"
    assert len(result['explanation']) > 0, \
        "Missing explanation"
    assert 'signals' in result, "Missing signals"

    print(f"  Stock: {result['stock_name']}")
    print(f"  Recommendation: {result['recommendation']}")
    print(f"  Confidence: {result['confidence']:.0%}")
    print(f"  Score: {result['score']}")
    print(f"  Risk: {result['risk_level']}")
    print(f"  Action: {result['suggested_action']}")
    print()
    print("  Signals:")
    for signal_name, signal_data in result['signals'].items():
        print(f"    - {signal_name}: {signal_data}")

    print("\n  [PASS] Recommendation engine works")
    return True


def test_user_profiles():
    """Test different user profiles"""
    print("\n" + "=" * 60)
    print("TEST 2: User Profiles")
    print("=" * 60)

    stock_code = 'TN0001600154'
    profiles = ['conservative', 'moderate', 'aggressive']

    for profile in profiles:
        result = make_recommendation(stock_code, user_profile=profile)
        print(f"  {profile.upper()}: {result['recommendation']} "
              f"(score: {result['score']:.2f}, conf: {result['confidence']:.0%})")

    print("\n  [PASS] User profiles work correctly")
    return True


def test_portfolio_operations():
    """Test portfolio buy/sell operations"""
    print("\n" + "=" * 60)
    print("TEST 3: Portfolio Operations")
    print("=" * 60)

    # Create portfolio
    p = Portfolio(initial_capital=10000, name="Test Portfolio")
    print(f"  Initial capital: {p.cash:.2f} TND")

    # Buy stocks
    result1 = p.buy('TN0001600154', 'ATTIJARI BANK', price=51.50, quantity=50, date='2026-02-07')
    print(f"  Buy ATTIJARI: {result1['message']}")
    assert result1['success'], "Buy should succeed"

    result2 = p.buy('TN0001800457', 'BIAT', price=93.90, quantity=20, date='2026-02-07')
    print(f"  Buy BIAT: {result2['message']}")
    assert result2['success'], "Buy should succeed"

    # Check portfolio
    current_prices = {
        'TN0001600154': 53.00,  # Up from 51.50
        'TN0001800457': 92.50   # Down from 93.90
    }

    metrics = p.get_performance_metrics(current_prices)
    print(f"\n  Portfolio Value: {metrics['total_value']:.2f} TND")
    print(f"  Cash: {metrics['cash']:.2f} TND")
    print(f"  Holdings: {metrics['holdings_value']:.2f} TND")
    print(f"  ROI: {metrics['roi_percentage']:+.2f}%")

    # Test positions
    positions = p.get_position_details(current_prices)
    print(f"\n  Positions ({len(positions)}):")
    for pos in positions:
        print(f"    - {pos['stock_name']}: {pos['quantity']} @ {pos['avg_price']:.2f} "
              f"-> {pos['current_price']:.2f} ({pos['gain_loss_pct']:+.1f}%)")

    # Test sell
    result3 = p.sell('TN0001600154', price=53.00, quantity=25, date='2026-02-07')
    print(f"\n  Sell 25 ATTIJARI: {result3['message']}")
    assert result3['success'], "Sell should succeed"

    # Check updated metrics
    metrics = p.get_performance_metrics(current_prices)
    print(f"  Updated ROI: {metrics['roi_percentage']:+.2f}%")
    print(f"  Win rate: {metrics['win_rate']:.1f}%")

    # Test allocation
    allocation = p.get_allocation(current_prices)
    print(f"\n  Allocation:")
    for asset, pct in allocation.items():
        print(f"    - {asset}: {pct:.1f}%")

    print("\n  [PASS] Portfolio operations work correctly")
    return True


def test_insufficient_funds():
    """Test error handling for insufficient funds"""
    print("\n" + "=" * 60)
    print("TEST 4: Error Handling")
    print("=" * 60)

    p = Portfolio(initial_capital=1000)

    # Try to buy more than we can afford
    result = p.buy('TN0001600154', 'ATTIJARI BANK', price=51.50, quantity=100, date='2026-02-07')
    print(f"  Buy 100 shares @ 51.50 TND with 1000 TND:")
    print(f"    Success: {result['success']}")
    print(f"    Message: {result['message']}")

    assert not result['success'], "Should fail due to insufficient funds"

    # Try to sell stock we don't own
    result = p.sell('TN0001800457', price=90.0, quantity=10, date='2026-02-07')
    print(f"\n  Sell stock we don't own:")
    print(f"    Success: {result['success']}")
    print(f"    Message: {result['message']}")

    assert not result['success'], "Should fail - don't own stock"

    print("\n  [PASS] Error handling works correctly")
    return True


def test_explainability():
    """Test explanation generation"""
    print("\n" + "=" * 60)
    print("TEST 5: Explainability System")
    print("=" * 60)

    result = make_recommendation('TN0001600154', user_profile='moderate')

    print("  Short explanation:")
    print(f"    {result['short_explanation']}")

    print("\n  Full explanation (first 500 chars):")
    explanation = result['explanation']
    print("    " + explanation[:500].replace('\n', '\n    '))

    assert len(explanation) > 100, "Explanation should be detailed"

    print("\n  [PASS] Explainability system works")
    return True


def test_batch_analysis():
    """Test batch analysis functions"""
    print("\n" + "=" * 60)
    print("TEST 6: Batch Analysis")
    print("=" * 60)

    # Test top recommendations
    print("  Top 3 BUY recommendations:")
    top_buys = get_top_recommendations(n=3, recommendation_type='buy')
    for rec in top_buys:
        print(f"    - {rec['stock_name']}: {rec['recommendation']} "
              f"(score: {rec['score']:.2f})")

    # Test market summary
    print("\n  Market Summary:")
    summary = get_market_summary()
    print(f"    Overall sentiment: {summary['overall_sentiment']}")
    print(f"    BUY signals: {summary['buy_signals']}")
    print(f"    SELL signals: {summary['sell_signals']}")
    print(f"    HOLD signals: {summary['hold_signals']}")

    if summary['alerts']:
        print(f"    Alerts: {len(summary['alerts'])}")
        for alert in summary['alerts'][:3]:
            print(f"      - {alert}")

    print("\n  [PASS] Batch analysis works")
    return True


def test_portfolio_with_recommendations():
    """Test using recommendations to build a portfolio"""
    print("\n" + "=" * 60)
    print("TEST 7: Recommendation-Driven Trading")
    print("=" * 60)

    # Get buy recommendations
    buys = get_top_recommendations(n=3, recommendation_type='buy')

    # Create portfolio and execute trades
    p = Portfolio(initial_capital=10000, name="Strategy Portfolio")

    from modules.decision.mocks import get_current_price_mock

    print("  Executing buy recommendations:")
    for rec in buys:
        price = get_current_price_mock(rec['stock_code'])
        quantity = int(1000 / price)  # ~1000 TND per position

        if quantity > 0:
            result = p.buy(
                rec['stock_code'],
                rec['stock_name'],
                price=price,
                quantity=quantity,
                date='2026-02-07'
            )
            if result['success']:
                print(f"    [OK] Bought {quantity} {rec['stock_name']} "
                      f"(rec: {rec['recommendation']}, conf: {rec['confidence']:.0%})")

    # Show portfolio
    current_prices = {rec['stock_code']: get_current_price_mock(rec['stock_code'])
                      for rec in buys}
    metrics = p.get_performance_metrics(current_prices)
    print(f"\n  Portfolio after trades:")
    print(f"    Value: {metrics['total_value']:.2f} TND")
    print(f"    Positions: {metrics['num_positions']}")
    print(f"    Cash remaining: {metrics['cash']:.2f} TND")

    print("\n  [PASS] Recommendation-driven trading works")
    return True


def run_all_tests():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("  DECISION ENGINE - INTEGRATION TESTS")
    print("  IHEC CODELAB 2.0 Hackathon")
    print("=" * 60)

    tests = [
        test_recommendation_engine,
        test_user_profiles,
        test_portfolio_operations,
        test_insufficient_funds,
        test_explainability,
        test_batch_analysis,
        test_portfolio_with_recommendations,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"\n  [FAIL] {test.__name__}: {e}")
            failed += 1

    print("\n" + "=" * 60)
    print(f"  RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)

    if failed == 0:
        print("\n  YOUR MODULE IS READY FOR INTEGRATION!")
        print("  Next steps:")
        print("  1. Share the API with your teammates")
        print("  2. Start building the dashboard")
        print("  3. Replace mocks with real module calls")
    else:
        print("\n  Some tests failed. Please fix before proceeding.")

    return failed == 0


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
