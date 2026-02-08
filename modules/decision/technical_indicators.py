"""
Technical Indicators
====================
RSI and MACD calculations for BVMT Trading Assistant.
"""

from typing import Dict, Optional

import numpy as np
import pandas as pd


def calculate_rsi(df: pd.DataFrame, period: int = 14) -> Optional[float]:
    """
    Calculate the Relative Strength Index (RSI).

    Args:
        df: DataFrame with a 'close' column.
        period: Lookback period for RSI (default 14).

    Returns:
        Current RSI value (0-100), or None if insufficient data.
    """
    if df is None or 'close' not in df.columns:
        return None

    closes = df['close'].astype(float)
    if len(closes) < period + 1:
        return None

    delta = closes.diff()
    gains = delta.clip(lower=0)
    losses = -delta.clip(upper=0)

    avg_gain = gains.rolling(window=period, min_periods=period).mean()
    avg_loss = losses.rolling(window=period, min_periods=period).mean()

    latest_gain = avg_gain.iloc[-1]
    latest_loss = avg_loss.iloc[-1]

    if np.isnan(latest_gain) or np.isnan(latest_loss):
        return None

    if latest_loss == 0:
        return 100.0

    rs = latest_gain / latest_loss
    rsi = 100.0 - (100.0 / (1.0 + rs))
    return float(rsi)


def calculate_macd(df: pd.DataFrame) -> Optional[Dict[str, float]]:
    """
    Calculate MACD, Signal line, and Histogram.

    Args:
        df: DataFrame with a 'close' column.

    Returns:
        Dict with macd, signal, histogram, and trend, or None if insufficient data.
    """
    if df is None or 'close' not in df.columns:
        return None

    closes = df['close'].astype(float)
    if len(closes) < 26:
        return None

    ema12 = closes.ewm(span=12, adjust=False).mean()
    ema26 = closes.ewm(span=26, adjust=False).mean()
    macd_line = ema12 - ema26
    signal_line = macd_line.ewm(span=9, adjust=False).mean()
    histogram = macd_line - signal_line

    macd_value = macd_line.iloc[-1]
    signal_value = signal_line.iloc[-1]
    hist_value = histogram.iloc[-1]

    if np.isnan(macd_value) or np.isnan(signal_value) or np.isnan(hist_value):
        return None

    trend = 'bullish' if hist_value > 0 else 'bearish'
    return {
        'macd': float(macd_value),
        'signal': float(signal_value),
        'histogram': float(hist_value),
        'trend': trend
    }
