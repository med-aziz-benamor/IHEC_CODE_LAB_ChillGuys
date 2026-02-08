"""
Stock Data Loader
Loads and provides access to BVMT historical stock data.
"""

import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime, timedelta

# Cache for loaded data
_stock_cache: Dict[str, pd.DataFrame] = {}
_all_stocks_cache: Optional[pd.DataFrame] = None

# Stock name mapping (ISIN -> Name)
STOCK_NAMES = {
    'TN0001100254': 'SFBT',
    'TN0001400704': 'SPDIT - SICAF',
    'TN0001600154': 'ATTIJARI BANK',
    'TN0001800457': 'BIAT',
    'TN0001800556': 'BT',
    'TN0001800853': 'BH',
    'TN0001900604': 'TUNISAIR',
    'TN0002200204': 'SOTUMAG',
    'TN0003600154': 'AMEN BANK',
    'TN0003800200': 'STB',
    'TN0004900255': 'UIB',
    'TN0005900304': 'MONOPRIX',
    'TN0006700406': 'POULINA',
    'TN0007100507': 'DELICE HOLDING',
    'TN0007800405': 'CARTHAGE CEMENT',
    'TN0008500400': 'SAH',
    'TN0009100309': 'ONE TECH HOLDING',
    'TN0009200406': 'TELNET HOLDING',
}


def get_data_path() -> Path:
    """Get the path to the data directory"""
    return Path(__file__).parent.parent.parent / 'data'


def load_all_stocks() -> pd.DataFrame:
    """Load all stock data from CSV files"""
    global _all_stocks_cache

    if _all_stocks_cache is not None:
        return _all_stocks_cache

    data_path = get_data_path()
    all_data = []

    # Load CSV files (2022-2025)
    for year in [2022, 2023, 2024, 2025]:
        file_path = data_path / f'histo_cotation_{year}.csv'
        if file_path.exists():
            try:
                df = pd.read_csv(file_path, sep=';', encoding='utf-8')
                # Clean column names
                df.columns = [col.strip() for col in df.columns]
                all_data.append(df)
            except Exception as e:
                print(f"Error loading {file_path}: {e}")

    if not all_data:
        raise FileNotFoundError("No stock data files found")

    # Combine all data
    combined = pd.concat(all_data, ignore_index=True)

    # Clean and format data
    combined['SEANCE'] = pd.to_datetime(combined['SEANCE'].str.strip(), format='%d/%m/%Y', errors='coerce')
    combined['CODE'] = combined['CODE'].str.strip()
    combined['VALEUR'] = combined['VALEUR'].str.strip()

    # Convert numeric columns
    for col in ['OUVERTURE', 'CLOTURE', 'PLUS_BAS', 'PLUS_HAUT', 'QUANTITE_NEGOCIEE', 'CAPITAUX']:
        combined[col] = pd.to_numeric(combined[col].astype(str).str.replace(',', '.').str.strip(), errors='coerce')

    combined = combined.sort_values('SEANCE')
    _all_stocks_cache = combined

    return combined


def get_stock_data(stock_code: str, days: int = 30) -> pd.DataFrame:
    """Get recent data for a specific stock"""
    all_data = load_all_stocks()

    stock_data = all_data[all_data['CODE'] == stock_code].copy()
    stock_data = stock_data.sort_values('SEANCE', ascending=False).head(days)
    stock_data = stock_data.sort_values('SEANCE')

    return stock_data


def get_stock_name(stock_code: str) -> str:
    """Get the name of a stock from its ISIN code"""
    if stock_code in STOCK_NAMES:
        return STOCK_NAMES[stock_code]

    # Try to get from data
    all_data = load_all_stocks()
    stock_data = all_data[all_data['CODE'] == stock_code]

    if not stock_data.empty:
        name = stock_data['VALEUR'].iloc[0]
        STOCK_NAMES[stock_code] = name  # Cache it
        return name

    return stock_code


def get_current_price(stock_code: str) -> float:
    """Get the most recent closing price for a stock"""
    stock_data = get_stock_data(stock_code, days=5)

    if stock_data.empty:
        return 0.0

    return float(stock_data['CLOTURE'].iloc[-1])


def get_all_stock_codes() -> List[str]:
    """Get list of all available stock codes"""
    all_data = load_all_stocks()
    return sorted(all_data['CODE'].unique().tolist())


def get_price_history(stock_code: str, days: int = 30) -> List[Dict]:
    """Get price history as a list of dicts for charts"""
    stock_data = get_stock_data(stock_code, days)

    history = []
    for _, row in stock_data.iterrows():
        history.append({
            'date': row['SEANCE'].strftime('%Y-%m-%d') if pd.notna(row['SEANCE']) else None,
            'open': float(row['OUVERTURE']) if pd.notna(row['OUVERTURE']) else None,
            'close': float(row['CLOTURE']) if pd.notna(row['CLOTURE']) else None,
            'high': float(row['PLUS_HAUT']) if pd.notna(row['PLUS_HAUT']) else None,
            'low': float(row['PLUS_BAS']) if pd.notna(row['PLUS_BAS']) else None,
            'volume': int(row['QUANTITE_NEGOCIEE']) if pd.notna(row['QUANTITE_NEGOCIEE']) else 0,
        })

    return history


def calculate_rsi(stock_code: str, period: int = 14) -> Optional[float]:
    """Calculate RSI (Relative Strength Index) for a stock"""
    stock_data = get_stock_data(stock_code, days=period + 10)

    if len(stock_data) < period + 1:
        return None

    # Calculate price changes
    prices = stock_data['CLOTURE'].values
    deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]

    # Separate gains and losses
    gains = [d if d > 0 else 0 for d in deltas]
    losses = [-d if d < 0 else 0 for d in deltas]

    # Calculate average gain and loss
    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period

    if avg_loss == 0:
        return 100.0

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return rsi


def get_volatility(stock_code: str, days: int = 20) -> float:
    """Calculate price volatility (standard deviation of returns)"""
    stock_data = get_stock_data(stock_code, days=days)

    if len(stock_data) < 2:
        return 0.0

    prices = stock_data['CLOTURE'].values
    returns = [(prices[i] - prices[i-1]) / prices[i-1] for i in range(1, len(prices)) if prices[i-1] != 0]

    if not returns:
        return 0.0

    mean_return = sum(returns) / len(returns)
    variance = sum((r - mean_return) ** 2 for r in returns) / len(returns)

    return variance ** 0.5


def get_current_prices_dict(stock_codes: List[str] = None) -> Dict[str, float]:
    """Get current prices for multiple stocks as a dict"""
    if stock_codes is None:
        stock_codes = list(STOCK_NAMES.keys())

    prices = {}
    for code in stock_codes:
        price = get_current_price(code)
        if price > 0:
            prices[code] = price

    return prices


def get_top_stocks(n: int = 10) -> List[Dict]:
    """Get top N stocks by trading volume"""
    all_data = load_all_stocks()

    # Get the most recent date
    latest_date = all_data['SEANCE'].max()

    # Filter to recent data (last 5 trading days)
    recent = all_data[all_data['SEANCE'] >= latest_date - timedelta(days=7)]

    # Aggregate by stock
    summary = recent.groupby('CODE').agg({
        'VALEUR': 'first',
        'CLOTURE': 'last',
        'QUANTITE_NEGOCIEE': 'sum',
        'CAPITAUX': 'sum'
    }).reset_index()

    # Sort by volume
    summary = summary.sort_values('CAPITAUX', ascending=False).head(n)

    result = []
    for _, row in summary.iterrows():
        result.append({
            'code': row['CODE'],
            'name': row['VALEUR'],
            'price': float(row['CLOTURE']) if pd.notna(row['CLOTURE']) else 0,
            'volume': int(row['QUANTITE_NEGOCIEE']) if pd.notna(row['QUANTITE_NEGOCIEE']) else 0,
        })

    return result
