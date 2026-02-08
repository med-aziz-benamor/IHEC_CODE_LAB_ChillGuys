"""
Integration Example for Decision Module
========================================

This shows how Aziz's decision module can use the forecasting module.

Author: Forecasting Team
"""

import sys
sys.path.append('modules')

from forecasting.predict import predict_next_days
from shared.data_loader import BVMTDataLoader
import json


def example_single_stock():
    """Example: Get predictions for a single stock"""
    
    print("\n" + "="*70)
    print("EXAMPLE 1: Single Stock Prediction")
    print("="*70)
    
    # Use the predict_next_days function
    stock_code = 'TN0001100254'  # BH BANK
    
    result = predict_next_days(
        stock_code=stock_code,
        n_days=5
    )
    
    if 'error' in result:
        print(f"❌ Error: {result['error']}")
        return
    
    print(f"\n📊 Stock: {result['stock_name']} ({result['stock_code']})")
    print(f"   Model: {result['model_used']}")
    print(f"   Last actual price: {result['last_actual_close']:.2f} TND ({result['last_actual_date']})")
    
    print(f"\n🔮 Predictions for next 5 days:")
    for pred in result['predictions']:
        trend = "↑" if pred['predicted_close'] > result['last_actual_close'] else "↓"
        print(f"   {pred['date']}: {pred['predicted_close']:.2f} TND {trend} (confidence: {pred['confidence']:.0%})")
    
    print(f"\n📈 Model Performance:")
    print(f"   RMSE: {result['metrics']['rmse']:.3f} TND")
    print(f"   MAE: {result['metrics']['mae']:.3f} TND")
    print(f"   Directional Accuracy: {result['metrics']['directional_accuracy']:.1%}")


def example_multiple_stocks():
    """Example: Get predictions for multiple stocks (for portfolio analysis)"""
    
    print("\n" + "="*70)
    print("EXAMPLE 2: Multiple Stocks (Portfolio Analysis)")
    print("="*70)
    
    # Load data to get top stocks
    loader = BVMTDataLoader('web_histo_cotation_2022.csv')
    top_stocks = loader.get_top_liquid_stocks(3)
    
    portfolio_predictions = {}
    
    for stock in top_stocks:
        stock_code = stock['stock_code']
        
        print(f"\n📊 Processing {stock['stock_name']}...")
        
        result = predict_next_days(stock_code, n_days=5)
        
        if 'error' not in result:
            portfolio_predictions[stock_code] = result
            
            # Calculate expected return
            current_price = result['last_actual_close']
            avg_predicted = sum(p['predicted_close'] for p in result['predictions']) / len(result['predictions'])
            expected_return = (avg_predicted - current_price) / current_price * 100
            
            print(f"   Current: {current_price:.2f} TND")
            print(f"   5-day avg prediction: {avg_predicted:.2f} TND")
            print(f"   Expected return: {expected_return:+.2f}%")
    
    return portfolio_predictions


def example_decision_logic():
    """Example: Use predictions in a simple trading decision logic"""
    
    print("\n" + "="*70)
    print("EXAMPLE 3: Trading Decision Logic")
    print("="*70)
    
    loader = BVMTDataLoader('web_histo_cotation_2022.csv')
    top_stocks = loader.get_top_liquid_stocks(3)
    
    recommendations = []
    
    for stock in top_stocks:
        stock_code = stock['stock_code']
        stock_name = stock['stock_name']
        
        result = predict_next_days(stock_code, n_days=5)
        
        if 'error' in result:
            continue
        
        current_price = result['last_actual_close']
        predictions = [p['predicted_close'] for p in result['predictions']]
        avg_confidence = sum(p['confidence'] for p in result['predictions']) / len(result['predictions'])
        
        # Calculate trend
        trend_pct = (predictions[-1] - current_price) / current_price * 100
        
        # Simple decision logic
        if trend_pct > 2 and avg_confidence > 0.7:
            action = "STRONG BUY"
            signal_strength = "🟢🟢🟢"
        elif trend_pct > 0.5 and avg_confidence > 0.6:
            action = "BUY"
            signal_strength = "🟢🟢"
        elif trend_pct < -2 and avg_confidence > 0.7:
            action = "STRONG SELL"
            signal_strength = "🔴🔴🔴"
        elif trend_pct < -0.5 and avg_confidence > 0.6:
            action = "SELL"
            signal_strength = "🔴🔴"
        else:
            action = "HOLD"
            signal_strength = "🟡"
        
        recommendations.append({
            'stock_code': stock_code,
            'stock_name': stock_name,
            'current_price': current_price,
            'predicted_trend': trend_pct,
            'confidence': avg_confidence,
            'action': action,
            'signal_strength': signal_strength
        })
    
    print("\n💡 Trading Recommendations:")
    print("-" * 70)
    for rec in recommendations:
        print(f"{rec['signal_strength']} {rec['stock_name'][:25]:25s} | {rec['action']:12s} | "
              f"Current: {rec['current_price']:6.2f} TND | "
              f"Trend: {rec['predicted_trend']:+5.1f}% | "
              f"Conf: {rec['confidence']:.0%}")
    
    return recommendations


def example_cached_predictions():
    """Example: Use pre-cached predictions for fast demo"""
    
    print("\n" + "="*70)
    print("EXAMPLE 4: Using Cached Predictions (Fast Demo)")
    print("="*70)
    
    try:
        with open('modules/forecasting/demo_predictions.json', 'r') as f:
            cached = json.load(f)
        
        print(f"\n📦 Loaded {len(cached)} cached predictions")
        print("\nAvailable stocks:")
        
        for stock_code, data in list(cached.items())[:3]:
            print(f"   {data['stock_name']}: {len(data['predictions'])} days, trend: {data['trend']}")
        
        return cached
        
    except FileNotFoundError:
        print("⚠️  Cache file not found. Run forecasting_backtest.ipynb first.")
        return None


def main():
    """Run all examples"""
    
    print("\n" + "="*70)
    print("FORECASTING MODULE - INTEGRATION EXAMPLES")
    print("For: Aziz's Decision Module")
    print("="*70)
    
    try:
        # Example 1: Single stock
        example_single_stock()
        
        # Example 2: Multiple stocks
        portfolio = example_multiple_stocks()
        
        # Example 3: Decision logic
        recommendations = example_decision_logic()
        
        # Example 4: Cached predictions
        cached = example_cached_predictions()
        
        print("\n" + "="*70)
        print("✅ ALL EXAMPLES COMPLETED")
        print("="*70)
        print("\n💡 Tips for Integration:")
        print("   1. Use predict_next_days() for real-time predictions")
        print("   2. Use cached predictions for demo (faster)")
        print("   3. Always check for 'error' key in results")
        print("   4. Confidence scores decrease with prediction horizon")
        print("   5. Combine with sentiment & anomaly scores for best results")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
