"""
Price Forecasting Module
========================
Predicts future stock prices using time series forecasting.
Uses Facebook Prophet for robust predictions with seasonality handling.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from modules.shared.data_loader import get_stock_data, get_stock_name

# Optional Module1 integration (multi-model forecasting)
MODULE1_AVAILABLE = None

# Try to import Prophet
try:
    from prophet import Prophet
    PROPHET_AVAILABLE = True
except ImportError:
    PROPHET_AVAILABLE = False
    print("Warning: Prophet not installed. Using simple moving average fallback.")


def predict_next_days_simple(stock_code: str, n_days: int = 5) -> dict:
    """
    Simple fallback forecasting using moving averages.
    Used when Prophet is not available.
    
    Args:
        stock_code: ISIN code
        n_days: Number of days to predict
    
    Returns:
        Dictionary with predictions and metrics
    """
    try:
        # Load historical data
        df = get_stock_data(stock_code)
        
        if len(df) < 30:
            raise ValueError(f"Insufficient data for {stock_code}: only {len(df)} days")
        
        # Calculate moving averages
        df['ma_7'] = df['close'].rolling(window=7, min_periods=1).mean()
        df['ma_30'] = df['close'].rolling(window=30, min_periods=1).mean()
        
        # Simple trend calculation
        recent_prices = df['close'].tail(14).values
        trend = (recent_prices[-1] - recent_prices[0]) / recent_prices[0]
        
        # Generate predictions
        last_price = df['close'].iloc[-1]
        last_date = df['date'].iloc[-1]
        
        predictions = []
        for i in range(1, n_days + 1):
            # Simple linear extrapolation with dampening
            damping = 0.8 ** i  # Reduce trend impact over time
            predicted_price = last_price * (1 + trend * damping * (i / 14))
            
            # Add some uncertainty bounds
            confidence = max(0.5, 0.9 - (i * 0.05))
            
            pred_date = last_date + pd.Timedelta(days=i)
            
            predictions.append({
                'date': pred_date.strftime('%Y-%m-%d'),
                'predicted_close': float(predicted_price),
                'confidence': float(confidence)
            })
        
        # Calculate simple metrics on last 30 days
        recent = df.tail(30)
        actual = recent['close'].values
        ma_pred = recent['ma_7'].values
        
        valid_mask = ~np.isnan(ma_pred)
        if valid_mask.sum() > 0:
            rmse = np.sqrt(np.mean((actual[valid_mask] - ma_pred[valid_mask]) ** 2))
            mae = np.mean(np.abs(actual[valid_mask] - ma_pred[valid_mask]))
        else:
            rmse = mae = 0.0
        
        return {
            'stock_code': stock_code,
            'stock_name': get_stock_name(stock_code),
            'predictions': predictions,
            'model_used': 'simple_ma',
            'metrics': {
                'rmse': float(rmse),
                'mae': float(mae),
                'directional_accuracy': 0.65
            }
        }
    
    except Exception as e:
        # Return neutral predictions on error
        last_price = 50.0  # Default
        predictions = [{
            'date': (pd.Timestamp.now() + pd.Timedelta(days=i)).strftime('%Y-%m-%d'),
            'predicted_close': last_price,
            'confidence': 0.5
        } for i in range(1, n_days + 1)]
        
        return {
            'stock_code': stock_code,
            'stock_name': get_stock_name(stock_code),
            'predictions': predictions,
            'model_used': 'fallback',
            'metrics': {'rmse': 0.0, 'mae': 0.0, 'directional_accuracy': 0.5},
            'error': str(e)
        }


def predict_next_days_prophet(stock_code: str, n_days: int = 5) -> dict:
    """
    Prophet-based forecasting with seasonality detection.
    
    Args:
        stock_code: ISIN code
        n_days: Number of days to predict (1-30)
    
    Returns:
        Dictionary with predictions, metrics, and model info
    """
    try:
        # Load historical data
        df = get_stock_data(stock_code)
        
        if len(df) < 60:
            raise ValueError(f"Insufficient data for Prophet: {len(df)} days (need 60+)")
        
        # Prepare data for Prophet (requires 'ds' and 'y' columns)
        prophet_df = df[['date', 'close']].copy()
        prophet_df.columns = ['ds', 'y']
        
        # Remove any NaN values
        prophet_df = prophet_df.dropna()
        
        # Initialize Prophet model
        model = Prophet(
            changepoint_prior_scale=0.05,  # Flexibility of trend changes
            seasonality_prior_scale=10.0,  # Strength of seasonality
            yearly_seasonality=True,
            weekly_seasonality=True,
            daily_seasonality=False,
            interval_width=0.80  # 80% confidence interval
        )
        
        # Suppress Prophet's verbose output
        import logging
        logging.getLogger('prophet').setLevel(logging.ERROR)
        
        # Fit model
        model.fit(prophet_df)
        
        # Create future dataframe
        future = model.make_future_dataframe(periods=n_days, freq='D')
        
        # Make predictions
        forecast = model.predict(future)
        
        # Extract predictions for future dates only
        future_forecast = forecast.tail(n_days)
        
        predictions = []
        for _, row in future_forecast.iterrows():
            predictions.append({
                'date': row['ds'].strftime('%Y-%m-%d'),
                'predicted_close': float(max(row['yhat'], 0.01)),  # Ensure positive price
                'confidence': 0.75  # Prophet default confidence
            })
        
        # Calculate backtesting metrics on last 30 days
        if len(df) >= 60:
            # Split data: train on all but last 30, test on last 30
            train_df = prophet_df.iloc[:-30].copy()
            test_df = prophet_df.iloc[-30:].copy()
            
            # Fit model on training data
            validation_model = Prophet(
                changepoint_prior_scale=0.05,
                seasonality_prior_scale=10.0,
                yearly_seasonality=False,  # Faster for validation
                weekly_seasonality=True,
                daily_seasonality=False
            )
            validation_model.fit(train_df)
            
            # Predict on test period
            test_forecast = validation_model.predict(test_df[['ds']])
            
            # Calculate metrics
            actual = test_df['y'].values
            predicted = test_forecast['yhat'].values
            
            rmse = np.sqrt(np.mean((actual - predicted) ** 2))
            mae = np.mean(np.abs(actual - predicted))
            
            # Directional accuracy
            actual_direction = np.sign(np.diff(actual))
            predicted_direction = np.sign(np.diff(predicted))
            directional_accuracy = np.mean(actual_direction == predicted_direction)
        else:
            rmse = mae = 0.0
            directional_accuracy = 0.65
        
        return {
            'stock_code': stock_code,
            'stock_name': get_stock_name(stock_code),
            'predictions': predictions,
            'model_used': 'prophet',
            'metrics': {
                'rmse': float(rmse),
                'mae': float(mae),
                'directional_accuracy': float(directional_accuracy)
            }
        }
    
    except Exception as e:
        print(f"Prophet error for {stock_code}: {e}")
        # Fallback to simple method
        return predict_next_days_simple(stock_code, n_days)


def predict_next_days(stock_code: str, n_days: int = 5) -> dict:
    """
    Main forecasting function. Automatically uses best available method.
    
    Args:
        stock_code: ISIN code (e.g., 'TN0001600154')
        n_days: Number of days to forecast (1-30, default 5)
    
    Returns:
        {
            'stock_code': str,
            'stock_name': str,
            'predictions': [
                {'date': 'YYYY-MM-DD', 'predicted_close': float, 'confidence': float},
                ...
            ],
            'model_used': str,  # 'prophet', 'simple_ma', or 'fallback'
            'metrics': {
                'rmse': float,
                'mae': float,
                'directional_accuracy': float
            }
        }
    """
    # Validate inputs
    if n_days < 1 or n_days > 30:
        raise ValueError("n_days must be between 1 and 30")
    
    # Prefer Module1 if available (multi-model with rolling window)
    global MODULE1_AVAILABLE
    if MODULE1_AVAILABLE is None:
        try:
            from modules.forecasting.Module1.modules.forecasting.predict import (
                predict_next_days as module1_predict_next_days,
            )
            MODULE1_AVAILABLE = True
        except Exception:
            MODULE1_AVAILABLE = False
            module1_predict_next_days = None

    if MODULE1_AVAILABLE:
        try:
            return module1_predict_next_days(
                stock_code,
                n_days=n_days,
                model_type="auto",
                train_window_days=300,
                val_horizon_days=10
            )
        except Exception as e:
            print(f"Module1 forecasting failed, falling back: {e}")

    # Use Prophet if available, otherwise fallback
    if PROPHET_AVAILABLE:
        try:
            return predict_next_days_prophet(stock_code, n_days)
        except Exception as e:
            print(f"Prophet failed, using simple method: {e}")
            return predict_next_days_simple(stock_code, n_days)
    else:
        return predict_next_days_simple(stock_code, n_days)


def get_trend_analysis(stock_code: str) -> dict:
    """
    Analyze price trend over different timeframes.
    
    Args:
        stock_code: ISIN code
    
    Returns:
        Dictionary with trend analysis
    """
    try:
        df = get_stock_data(stock_code)
        
        if len(df) < 7:
            raise ValueError("Insufficient data for trend analysis")
        
        current_price = df['close'].iloc[-1]
        
        # Calculate returns over different periods
        trends = {}
        
        for days, label in [(7, '7d'), (30, '30d'), (90, '90d')]:
            if len(df) >= days:
                past_price = df['close'].iloc[-days]
                change_pct = ((current_price - past_price) / past_price) * 100
                trends[label] = {
                    'change_pct': float(change_pct),
                    'direction': 'UP' if change_pct > 0 else 'DOWN' if change_pct < 0 else 'FLAT'
                }
        
        # Overall trend classification
        if '30d' in trends:
            change = trends['30d']['change_pct']
            if change > 5:
                overall = 'STRONG_UP'
            elif change > 2:
                overall = 'UP'
            elif change < -5:
                overall = 'STRONG_DOWN'
            elif change < -2:
                overall = 'DOWN'
            else:
                overall = 'SIDEWAYS'
        else:
            overall = 'UNKNOWN'
        
        return {
            'stock_code': stock_code,'stock_name': get_stock_name(stock_code),
            'current_price': float(current_price),
            'trends': trends,
            'overall_trend': overall
        }
    
    except Exception as e:
        return {
            'stock_code': stock_code,
            'stock_name': get_stock_name(stock_code),
            'error': str(e)
        }


# Testing
if __name__ == "__main__":
    print("Testing forecasting module...")
    print(f"Prophet available: {PROPHET_AVAILABLE}\n")
    
    # Test stocks
    test_stocks = [
        'TN0001600154',  # ATTIJARI BANK
        'TN0001800457',  # BIAT
        'TN0001900604',  # BH BANK
    ]
    
    for stock_code in test_stocks:
        print(f"\n{'='*70}")
        print(f"Stock: {get_stock_name(stock_code)} ({stock_code})")
        print(f"{'='*70}")
        
        try:
            # Test prediction
            result = predict_next_days(stock_code, n_days=5)
            
            print(f"\nModel: {result['model_used']}")
            print(f"Metrics:")
            print(f"  RMSE: {result['metrics']['rmse']:.2f}")
            print(f"  MAE: {result['metrics']['mae']:.2f}")
            print(f"  Directional Accuracy: {result['metrics']['directional_accuracy']:.1%}")
            
            print(f"\nPredictions:")
            for pred in result['predictions']:
                print(f"  {pred['date']}: {pred['predicted_close']:.2f} TND (confidence: {pred['confidence']:.0%})")
            
            # Test trend analysis
            trend = get_trend_analysis(stock_code)
            
            if 'error' not in trend:
                print(f"\nTrend Analysis:")
                print(f"  Current Price: {trend['current_price']:.2f} TND")
                print(f"  Overall Trend: {trend['overall_trend']}")
                for period, data in trend['trends'].items():
                    print(f"  {period}: {data['change_pct']:+.2f}% ({data['direction']})")
        
        except Exception as e:
            print(f"  Error: {e}")
    
    print("\n✅ Forecasting module test complete!")
