"""
Shared data loader for BVMT Trading Assistant
Loads and cleans historical stock data from BVMT CSV files
"""

import pandas as pd
import numpy as np
from typing import Optional, List, Dict
from pathlib import Path
import os

# Stock name mapping for display (expand as needed)
STOCK_NAMES = {
    'TN0001600154': 'ATTIJARI BANK',
    'TN0001800457': 'BIAT',
    'TN0001900604': 'BH BANK',
    'TN0002200053': 'BT',
    'TN0002600955': 'STB',
    'TN0003100609': 'BNA',
    'TN0003400058': 'AMEN BANK',
    'TN0003600350': 'ATB',
    'TN0005700018': 'POULINA GP HOLDING',
    'TN0001100254': 'SFBT',
    'TN0003200755': 'ICF',
    'TN0009400151': 'TUNIS RE',
    'TN0004800056': 'SOTUVER',
    'TN0005800057': 'TUNISIE LEASING',
}

# Global cache for loaded data
_DATA_CACHE = None


def get_data_filepath() -> str:
    """Find the correct data file path"""
    # Try multiple possible locations
    possible_paths = [
        'data/histo_cotation_combined_2022_2025.csv',
        'data/web_histo_cotation_2022.csv',
        'data/raw/web_histo_cotation_2022.csv',
        '../data/web_histo_cotation_2022.csv',
        os.path.join(os.path.dirname(__file__), '../../data/web_histo_cotation_2022.csv'),
        os.path.join(os.path.dirname(__file__), '../forecasting/Module1/histo_cotation_combined_2022_2025.csv'),
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    # Default to first option
    return 'data/web_histo_cotation_2022.csv'


def load_full_dataset(filepath: Optional[str] = None, force_reload: bool = False) -> pd.DataFrame:
    """
    Load and clean the full BVMT dataset.
    
    Args:
        filepath: Path to CSV file. If None, uses default location.
        force_reload: If True, reload data even if cached.
    
    Returns:
        DataFrame with standardized column names and cleaned data.
    """
    global _DATA_CACHE
    
    # Return cached data if available
    if _DATA_CACHE is not None and not force_reload:
        return _DATA_CACHE.copy()
    
    if filepath is None:
        filepath = get_data_filepath()
    
    try:
        # Read CSV with semicolon separator
        # The file has spaces around semicolons, so we use sep with regex
        df = pd.read_csv(filepath, sep=r'\s*;\s*', engine='python')
        
        # Parse dates from DD/MM/YYYY format
        df['SEANCE'] = pd.to_datetime(df['SEANCE'], format='%d/%m/%Y', errors='coerce')
        
        # Rename columns to English
        df = df.rename(columns={
            'SEANCE': 'date',
            'GROUPE': 'group',
            'CODE': 'stock_code',
            'VALEUR': 'stock_name',
            'OUVERTURE': 'open',
            'CLOTURE': 'close',
            'PLUS_BAS': 'low',
            'PLUS_HAUT': 'high',
            'QUANTITE_NEGOCIEE': 'volume',
            'NB_TRANSACTION': 'num_transactions',
            'CAPITAUX': 'market_cap'
        })
        
        # Convert numeric columns (handle comma as decimal separator if present)
        numeric_cols = ['open', 'close', 'low', 'high', 'volume', 'num_transactions', 'market_cap']
        for col in numeric_cols:
            if col in df.columns:
                # Convert to numeric, coerce errors to NaN
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Remove rows with missing critical data
        df = df.dropna(subset=['date', 'stock_code', 'close'])
        
        # Sort by date and stock code
        df = df.sort_values(['stock_code', 'date']).reset_index(drop=True)
        
        # Update STOCK_NAMES mapping from data
        unique_stocks = df[['stock_code', 'stock_name']].drop_duplicates()
        for _, row in unique_stocks.iterrows():
            if row['stock_code'] not in STOCK_NAMES and pd.notna(row['stock_name']):
                STOCK_NAMES[row['stock_code']] = row['stock_name']
        
        # Cache the data
        _DATA_CACHE = df.copy()
        
        return df
    
    except FileNotFoundError:
        raise FileNotFoundError(f"Data file not found: {filepath}")
    except Exception as e:
        raise Exception(f"Error loading dataset: {str(e)}")


def get_stock_data(
    stock_code: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    min_volume: int = 1
) -> pd.DataFrame:
    """
    Get data for a specific stock.
    
    Args:
        stock_code: ISIN like 'TN0001600154'
        start_date: Optional 'YYYY-MM-DD' format
        end_date: Optional 'YYYY-MM-DD' format
    
    Returns:
        DataFrame with columns: date, stock_code, stock_name, open, close, high, low, volume, num_transactions
    """
    df = load_full_dataset()
    
    # Filter by stock code
    stock_df = df[df['stock_code'] == stock_code].copy()
    
    if stock_df.empty:
        raise ValueError(f"No data found for stock code: {stock_code}")
    
    # Filter by date range if provided
    if start_date:
        stock_df = stock_df[stock_df['date'] >= pd.to_datetime(start_date)]
    
    if end_date:
        stock_df = stock_df[stock_df['date'] <= pd.to_datetime(end_date)]

    # Filter by minimum volume if requested
    if min_volume and 'volume' in stock_df.columns:
        stock_df = stock_df[stock_df['volume'] >= min_volume]

    return stock_df.reset_index(drop=True)


def get_most_liquid_stocks(n: int = 15) -> pd.DataFrame:
    """
    Return top N most liquid stocks using volume/transactions/market cap.

    Returns:
        DataFrame with columns: code, name, trading_days, total_volume, total_transactions, total_market_cap, liq_score
    """
    df = load_full_dataset()
    if df.empty:
        return pd.DataFrame()

    d2 = df.copy()
    if 'volume' in d2.columns:
        d2 = d2[d2['volume'] > 0]

    agg = d2.groupby(['stock_code', 'stock_name']).agg({
        'date': 'count',
        'volume': 'sum',
        'num_transactions': 'sum',
        'market_cap': 'sum'
    }).rename(columns={
        'date': 'trading_days',
        'volume': 'total_volume',
        'num_transactions': 'total_transactions',
        'market_cap': 'total_market_cap'
    }).reset_index()

    agg['liq_score'] = (
        np.log1p(agg['total_volume']) +
        np.log1p(agg['total_transactions']) +
        0.5 * np.log1p(agg['total_market_cap'].fillna(0))
    )

    agg = agg.sort_values('liq_score', ascending=False).head(n)
    agg['code'] = agg['stock_code']
    agg['name'] = agg['stock_name']
    return agg


def get_all_stocks() -> List[str]:
    """
    Return list of all unique stock codes in the dataset.
    
    Returns:
        List of ISIN stock codes
    """
    df = load_full_dataset()
    return sorted(df['stock_code'].unique().tolist())


def get_liquid_stocks(min_avg_volume: int = 1000, min_days: int = 30) -> List[str]:
    """
    Return stocks with sufficient average volume and data points.
    
    Args:
        min_avg_volume: Minimum average daily volume
        min_days: Minimum number of trading days
    
    Returns:
        List of liquid stock codes
    """
    df = load_full_dataset()
    
    # Calculate average volume and count per stock
    stock_stats = df.groupby('stock_code').agg({
        'volume': 'mean',
        'date': 'count'
    }).rename(columns={'date': 'num_days'})
    
    # Filter by criteria
    liquid = stock_stats[
        (stock_stats['volume'] >= min_avg_volume) &
        (stock_stats['num_days'] >= min_days)
    ]
    
    return sorted(liquid.index.tolist())


def get_current_price(stock_code: str) -> float:
    """
    Get most recent closing price for a stock.
    
    Args:
        stock_code: ISIN code
    
    Returns:
        Most recent closing price
    """
    try:
        stock_df = get_stock_data(stock_code)
        if stock_df.empty:
            return 0.0
        return float(stock_df.iloc[-1]['close'])
    except Exception:
        return 0.0


def get_stock_name(stock_code: str) -> str:
    """
    Get display name for a stock code.
    
    Args:
        stock_code: ISIN code
    
    Returns:
        Stock name or code if name not found
    """
    return STOCK_NAMES.get(stock_code, stock_code)


def get_price_history(stock_code: str, days: int = 30) -> pd.DataFrame:
    """
    Get recent price history for a stock.
    
    Args:
        stock_code: ISIN code
        days: Number of recent days to retrieve
    
    Returns:
        DataFrame with recent price data
    """
    stock_df = get_stock_data(stock_code)
    
    if stock_df.empty:
        return pd.DataFrame()
    
    # Get last N days
    return stock_df.tail(days).reset_index(drop=True)


def get_stock_summary(stock_code: str) -> Dict:
    """
    Get summary statistics for a stock.
    
    Args:
        stock_code: ISIN code
    
    Returns:
        Dictionary with summary stats
    """
    try:
        stock_df = get_stock_data(stock_code)
        
        if stock_df.empty:
            return {}
        
        recent = stock_df.tail(30)
        
        return {
            'stock_code': stock_code,
            'stock_name': get_stock_name(stock_code),
            'current_price': float(stock_df.iloc[-1]['close']),
            'previous_close': float(stock_df.iloc[-2]['close']) if len(stock_df) > 1 else 0.0,
            'change_pct': ((stock_df.iloc[-1]['close'] - stock_df.iloc[-2]['close']) / stock_df.iloc[-2]['close'] * 100) if len(stock_df) > 1 else 0.0,
            'avg_volume_30d': float(recent['volume'].mean()),
            'avg_price_30d': float(recent['close'].mean()),
            'min_price_30d': float(recent['close'].min()),
            'max_price_30d': float(recent['close'].max()),
            'num_data_points': len(stock_df),
            'date_range': f"{stock_df['date'].min().strftime('%Y-%m-%d')} to {stock_df['date'].max().strftime('%Y-%m-%d')}"
        }
    except Exception as e:
        return {'error': str(e)}


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Engineer features for anomaly detection from stock data.
    Integrated from Module3 for ML-based anomaly detection.

    Features created:
    - price_change_pct: Daily price change percentage
    - volume_change_pct: Daily volume change percentage
    - volatility_7d: 7-day rolling standard deviation of returns
    - volume_ma_7d: 7-day moving average of volume
    - volume_ma_30d: 30-day moving average of volume
    - volume_ratio_7d: Current volume / 7-day MA
    - volume_ratio_30d: Current volume / 30-day MA
    - transaction_per_volume: Transactions per unit volume (manipulation indicator)
    - price_volume_corr: Recent price-volume correlation
    - high_low_spread_pct: Daily high-low spread as % of close

    Args:
        df: DataFrame with stock data

    Returns:
        DataFrame with additional feature columns
    """
    # Make a copy to avoid modifying original
    df = df.copy()

    # Group by stock for time-series features
    grouped = df.groupby('stock_code')

    # --- Price-based features ---
    # Daily returns
    df['price_change_pct'] = grouped['close'].transform(lambda x: x.pct_change())

    # Volatility (7-day rolling std of returns)
    df['volatility_7d'] = grouped['price_change_pct'].transform(
        lambda x: x.rolling(window=7, min_periods=3).std()
    )

    # High-low spread as % of close (intraday volatility)
    df['high_low_spread_pct'] = ((df['high'] - df['low']) / df['close']) * 100

    # --- Volume-based features ---
    # Volume change
    df['volume_change_pct'] = grouped['volume'].transform(lambda x: x.pct_change())

    # Volume moving averages
    df['volume_ma_7d'] = grouped['volume'].transform(
        lambda x: x.rolling(window=7, min_periods=3).mean()
    )
    df['volume_ma_30d'] = grouped['volume'].transform(
        lambda x: x.rolling(window=30, min_periods=10).mean()
    )

    # Volume ratios (spike detection)
    df['volume_ratio_7d'] = df['volume'] / (df['volume_ma_7d'] + 1e-6)
    df['volume_ratio_30d'] = df['volume'] / (df['volume_ma_30d'] + 1e-6)

    # --- Transaction features ---
    # Transactions per volume unit (low value = potential block trades)
    df['transaction_per_volume'] = df['num_transactions'] / (df['volume'] + 1)

    # Average transaction size
    df['avg_transaction_size'] = df['volume'] / (df['num_transactions'] + 1)

    # --- Price-Volume relationship ---
    # Rolling correlation between price change and volume (fix for pandas groupby behavior)
    df['price_volume_corr'] = 0.0  # Initialize
    for stock in df['stock_code'].unique():
        mask = df['stock_code'] == stock
        stock_data = df[mask]
        
        corr = stock_data['price_change_pct'].rolling(window=7, min_periods=5).corr(
            stock_data['volume_change_pct']
        )
        df.loc[mask, 'price_volume_corr'] = corr

    # --- Temporal features ---
    df['day_of_week'] = df['date'].dt.dayofweek
    df['day_of_month'] = df['date'].dt.day

    # Fill NaN with 0 for initial rows (no history yet)
    feature_cols = [
        'price_change_pct', 'volume_change_pct', 'volatility_7d',
        'volume_ma_7d', 'volume_ma_30d', 'volume_ratio_7d', 'volume_ratio_30d',
        'transaction_per_volume', 'avg_transaction_size', 'price_volume_corr',
        'high_low_spread_pct'
    ]

    for col in feature_cols:
        if col in df.columns:
            df[col] = df[col].fillna(0)

    # Replace inf with large values
    df = df.replace([np.inf, -np.inf], [1e6, -1e6])

    return df


def get_feature_columns() -> List[str]:
    """
    Get list of feature columns used for ML anomaly detection model.

    Returns:
        List of feature column names
    """
    return [
        'volume',
        'num_transactions',
        'price_change_pct',
        'volume_change_pct',
        'volatility_7d',
        'volume_ratio_7d',
        'volume_ratio_30d',
        'transaction_per_volume',
        'avg_transaction_size',
        'price_volume_corr',
        'high_low_spread_pct',
        'day_of_week'
    ]


# Convenience function for testing
if __name__ == "__main__":
    print("Testing data loader...")
    
    # Load dataset
    df = load_full_dataset()
    print(f"✓ Loaded {len(df)} rows")
    print(f"✓ Date range: {df['date'].min()} to {df['date'].max()}")
    print(f"✓ Number of stocks: {df['stock_code'].nunique()}")
    
    # Test feature engineering
    print("\n✓ Testing feature engineering...")
    df_features = engineer_features(df.head(1000))
    print(f"  Added features: {get_feature_columns()}")
    print(f"  Total columns: {len(df_features.columns)}")
    
    # Test specific stock
    stock_code = 'TN0001600154'  # ATTIJARI BANK
    stock_df = get_stock_data(stock_code)
    print(f"\n✓ ATTIJARI BANK: {len(stock_df)} data points")
    print(f"  Current price: {get_current_price(stock_code)}")
    
    # Test liquid stocks
    liquid = get_liquid_stocks()
    print(f"\n✓ Found {len(liquid)} liquid stocks")
    print(f"  Top 5: {[get_stock_name(s) for s in liquid[:5]]}")
    
    # Test summary
    summary = get_stock_summary(stock_code)
    print(f"\n✓ Summary for ATTIJARI BANK:")
    for key, value in summary.items():
        print(f"  {key}: {value}")
    
    print("\n✅ All tests passed!")
