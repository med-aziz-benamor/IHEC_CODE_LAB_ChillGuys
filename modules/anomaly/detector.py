"""
Anomaly Detection Module
========================
Detects unusual market behavior using ML (Isolation Forest) and statistical methods:
- Volume spikes
- Price gaps  
- Low liquidity events
- Price-volume divergence
- ML-detected anomalies

Integrated with Module3 advanced detection capabilities.
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional
import sys
from pathlib import Path

from .alert_manager import get_default_alert_manager

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from modules.shared.data_loader import get_stock_data, get_stock_name, engineer_features
from modules.anomaly.model import AnomalyDetectionModel

# Model path
MODEL_PATH = Path(__file__).parent.parent.parent / 'models' / 'anomaly_model.pkl'


def load_model() -> Optional[AnomalyDetectionModel]:
    """
    Load the trained anomaly detection model.

    Returns:
        Trained AnomalyDetectionModel instance, or None if not found
    """
    if not MODEL_PATH.exists():
        print(f"Warning: ML model not found at {MODEL_PATH}. Using statistical methods only.")
        return None

    try:
        return AnomalyDetectionModel.load(MODEL_PATH)
    except Exception as e:
        print(f"Warning: Failed to load ML model ({e}). Using statistical methods only.")
        return None


def detect_volume_spike(row: pd.Series, threshold_sigma: float = 2.5) -> Optional[Dict]:
    """
    Detect abnormal volume spikes using statistical threshold.
    Enhanced version from Module3.

    Args:
        row: DataFrame row with volume and volume_ma_30d
        threshold_sigma: Number of standard deviations for spike

    Returns:
        Anomaly dict if detected, None otherwise
    """
    if pd.isna(row.get('volume_ratio_30d')) or row['volume'] == 0:
        return None

    # Check if volume is significantly above 30-day average
    if row['volume_ratio_30d'] > (1 + threshold_sigma):
        severity = 'HIGH' if row['volume_ratio_30d'] > 5 else 'MEDIUM'

        return {
            'type': 'volume_spike',
            'severity': severity,
            'date': row['date'].strftime('%Y-%m-%d'),
            'description': f"Volume spike: {row['volume_ratio_30d']:.1f}x moyenne 30j (volume: {row['volume']:,.0f})",
            'metrics': {
                'actual_value': float(row['volume']),
                'volume_ratio': float(row['volume_ratio_30d']),
                'deviation_sigma': float(row['volume_ratio_30d'] - 1)
            }
        }

    return None


def detect_price_gap(row: pd.Series, prev_row: Optional[pd.Series] = None,
                     threshold_pct: float = 0.03, threshold_sigma: float = 2.0) -> Optional[Dict]:
    """
    Detect unusual price movements.
    Enhanced version from Module3 with volatility z-score.

    Args:
        row: Current DataFrame row
        prev_row: Previous row (for context)
        threshold_pct: Minimum percentage change (3%)
        threshold_sigma: Number of standard deviations

    Returns:
        Anomaly dict if detected, None otherwise
    """
    if pd.isna(row.get('price_change_pct')) or pd.isna(row.get('volatility_7d')):
        return None

    price_change = abs(row['price_change_pct'])

    # Check if price change is significant
    if price_change > threshold_pct:
        # Check if it's unusual relative to recent volatility
        if row['volatility_7d'] > 0:
            z_score = price_change / row['volatility_7d']

            if z_score > threshold_sigma:
                severity = 'HIGH' if z_score > 3 else 'MEDIUM'
                direction = 'hausse' if row['price_change_pct'] > 0 else 'baisse'

                return {
                    'type': 'price_gap',
                    'severity': severity,
                    'date': row['date'].strftime('%Y-%m-%d'),
                    'description': f"Variation anormale: {direction} de {abs(row['price_change_pct'])*100:.1f}% ({z_score:.1f}σ)",
                    'metrics': {
                        'actual_value': float(row['price_change_pct']),
                        'deviation_sigma': float(z_score),
                        'price': float(row['close'])
                    }
                }

    return None


def detect_low_liquidity(row: pd.Series, threshold_transactions: int = 5) -> Optional[Dict]:
    """
    Detect critically low liquidity days.
    From Module3.

    Args:
        row: DataFrame row
        threshold_transactions: Minimum transactions for normal liquidity

    Returns:
        Anomaly dict if detected, None otherwise
    """
    if row['num_transactions'] < threshold_transactions or row['volume'] == 0:
        severity = 'HIGH' if row['num_transactions'] == 0 else 'MEDIUM'

        return {
            'type': 'low_liquidity',
            'severity': severity,
            'date': row['date'].strftime('%Y-%m-%d'),
            'description': f"Liquidité très faible: {row['num_transactions']} transactions, volume: {row['volume']:,.0f}",
            'metrics': {
                'actual_value': float(row['num_transactions']),
                'volume': float(row['volume'])
            }
        }

    return None


def detect_price_volume_divergence(row: pd.Series, threshold_price: float = 0.03,
                                   threshold_volume: float = -0.3) -> Optional[Dict]:
    """
    Detect suspicious price-volume divergence (price up, volume down).
    From Module3.

    Args:
        row: DataFrame row
        threshold_price: Minimum price increase
        threshold_volume: Maximum volume decrease (negative)

    Returns:
        Anomaly dict if detected, None otherwise
    """
    if pd.isna(row.get('price_change_pct')) or pd.isna(row.get('volume_change_pct')):
        return None

    # Price up significantly but volume down
    if row['price_change_pct'] > threshold_price and row['volume_change_pct'] < threshold_volume:
        return {
            'type': 'price_volume_divergence',
            'severity': 'MEDIUM',
            'date': row['date'].strftime('%Y-%m-%d'),
            'description': f"Divergence: prix +{row['price_change_pct']*100:.1f}% mais volume {row['volume_change_pct']*100:.1f}%",
            'metrics': {
                'price_change': float(row['price_change_pct']),
                'volume_change': float(row['volume_change_pct'])
            }
        }

    return None


# Legacy function kept for compatibility
def _detect_price_gap_legacy(stock_df: pd.DataFrame, threshold_pct: float = 5.0, lookback: int = 30) -> List[Dict]:
    """
    Legacy price gap detection function (kept for compatibility).
    
    Args:
        stock_df: DataFrame with stock data
        threshold_pct: Minimum percentage change to flag
        lookback: Days to look back
    
    Returns:
        List of detected price gap anomalies
    """
    anomalies = []
    
    # Calculate day-to-day price changes
    stock_df['price_change_pct'] = stock_df['close'].pct_change() * 100
    
    # Check recent data only
    recent_df = stock_df.tail(lookback)
    
    for idx, row in recent_df.iterrows():
        if pd.isna(row['price_change_pct']):
            continue
        
        abs_change = abs(row['price_change_pct'])
        
        if abs_change > threshold_pct:
            direction = 'hausse' if row['price_change_pct'] > 0 else 'baisse'
            severity = 'HIGH' if abs_change > 10 else 'MEDIUM' if abs_change > 7 else 'LOW'
            
            anomalies.append({
                'type': 'price_gap',
                'severity': severity,
                'date': row['date'].strftime('%Y-%m-%d'),
                'description': f"Gap de prix important: {direction} de {abs_change:.1f}%",
                'metrics': {
                    'actual_value': float(row['close']),
                    'expected_value': float(row['close'] / (1 + row['price_change_pct'] / 100)),
                    'change_percent': float(row['price_change_pct']),
                    'deviation_sigma': abs_change / 5.0  # Normalized
                }
            })
    
    return anomalies


def _detect_low_liquidity_legacy(stock_df: pd.DataFrame, min_transactions: int = 5, lookback: int = 30) -> List[Dict]:
    """
    Legacy: Detect days with unusually low trading activity.
    (Replaced by row-based version for Module3 integration)
    
    Args:
        stock_df: DataFrame with stock data
        min_transactions: Minimum number of transactions expected
        lookback: Days to look back
    
    Returns:
        List of low liquidity anomalies
    """
    anomalies = []
    
    # Check if num_transactions column exists
    if 'num_transactions' not in stock_df.columns:
        return anomalies
    
    # Calculate average transactions
    avg_transactions = stock_df['num_transactions'].rolling(window=30, min_periods=10).mean()
    stock_df['avg_transactions'] = avg_transactions
    
    # Check recent data
    recent_df = stock_df.tail(lookback)
    
    for idx, row in recent_df.iterrows():
        if pd.isna(row['num_transactions']) or pd.isna(row['avg_transactions']):
            continue
        
        # Flag if transactions are very low
        if row['num_transactions'] < min_transactions:
            severity = 'HIGH' if row['num_transactions'] < 2 else 'MEDIUM' if row['num_transactions'] < 4 else 'LOW'
            
            anomalies.append({
                'type': 'low_liquidity',
                'severity': severity,
                'date': row['date'].strftime('%Y-%m-%d'),
                'description': f"Très faible liquidité: seulement {int(row['num_transactions'])} transactions",
                'metrics': {
                    'actual_value': float(row['num_transactions']),
                    'expected_value': float(row['avg_transactions']),
                    'deviation_sigma': (row['avg_transactions'] - row['num_transactions']) / max(row['avg_transactions'], 1),
                }
            })
        
        # Also flag if significantly below average
        elif row['avg_transactions'] > 0 and row['num_transactions'] < row['avg_transactions'] * 0.2:
            anomalies.append({
                'type': 'low_liquidity',
                'severity': 'MEDIUM',
                'date': row['date'].strftime('%Y-%m-%d'),
                'description': f"Liquidité réduite: {int(row['num_transactions'])} transactions (vs moyenne {row['avg_transactions']:.0f})",
                'metrics': {
                    'actual_value': float(row['num_transactions']),
                    'expected_value': float(row['avg_transactions']),
                    'deviation_sigma': (row['avg_transactions'] - row['num_transactions']) / max(row['avg_transactions'], 1),
                }
            })
    
    return anomalies


def detect_price_volatility(stock_df: pd.DataFrame, threshold_pct: float = 15.0, window: int = 7, lookback: int = 30) -> List[Dict]:
    """
    Detect periods of unusually high price volatility.
    
    Args:
        stock_df: DataFrame with stock data
        threshold_pct: Threshold for high volatility (% range)
        window: Days to calculate volatility over
        lookback: Days to look back for anomalies
    
    Returns:
        List of high volatility anomalies
    """
    anomalies = []
    
    # Calculate rolling volatility (high-low range as % of close)
    stock_df['volatility'] = ((stock_df['high'] - stock_df['low']) / stock_df['close']) * 100
    stock_df['volatility_ma'] = stock_df['volatility'].rolling(window=window, min_periods=3).mean()
    
    # Check recent data
    recent_df = stock_df.tail(lookback)
    
    for idx, row in recent_df.iterrows():
        if pd.isna(row['volatility_ma']):
            continue
        
        if row['volatility_ma'] > threshold_pct:
            severity = 'HIGH' if row['volatility_ma'] > 20 else 'MEDIUM'
            
            anomalies.append({
                'type': 'high_volatility',
                'severity': severity,
                'date': row['date'].strftime('%Y-%m-%d'),
                'description': f"Volatilité élevée: variation moyenne de {row['volatility_ma']:.1f}% sur {window} jours",
                'metrics': {
                    'actual_value': float(row['volatility_ma']),
                    'expected_value': 5.0,  # Normal volatility benchmark
                    'deviation_sigma': row['volatility_ma'] / 5.0,
                }
            })
    
    return anomalies


def calculate_anomaly_score(anomalies: List[Dict]) -> float:
    """
    Calculate overall anomaly score from 0 (normal) to 10 (extreme).
    
    Args:
        anomalies: List of detected anomalies
    
    Returns:
        Anomaly score (0-10)
    """
    if not anomalies:
        return 0.0
    
    # Weight by severity
    severity_weights = {
        'LOW': 1.0,
        'MEDIUM': 2.5,
        'HIGH': 5.0
    }
    
    # Weight by type (some are more critical)
    type_weights = {
        'volume_spike': 1.0,
        'price_gap': 1.5,
        'low_liquidity': 1.2,
        'high_volatility': 1.3
    }
    
    total_score = 0.0
    
    for anom in anomalies:
        severity_weight = severity_weights.get(anom['severity'], 1.0)
        type_weight = type_weights.get(anom['type'], 1.0)
        total_score += severity_weight * type_weight
    
    # Cap at 10
    return min(total_score, 10.0)


def determine_risk_level(score: float) -> str:
    """
    Determine risk level from anomaly score.
    
    Args:
        score: Anomaly score (0-10)
    
    Returns:
        Risk level: 'NORMAL', 'ELEVATED', or 'HIGH'
    """
    if score >= 7:
        return 'HIGH'
    elif score >= 3:
        return 'ELEVATED'
    else:
        return 'NORMAL'


def detect_anomalies(stock_code: str, lookback_days: int = 30, use_ml: bool = True) -> dict:
    """
    Main anomaly detection function.
    Enhanced with Module3's ML capabilities (Isolation Forest).
    
    Args:
        stock_code: ISIN code
        lookback_days: Number of recent days to analyze
        use_ml: Whether to use ML model (True) or statistical only (False)
    
    Returns:
        {
            'stock_code': str,
            'stock_name': str,
            'date': str,  # Analysis date
            'anomalies_detected': [
                {
                    'type': str,
                    'severity': str,
                    'date': str,
                    'description': str,
                    'metrics': dict
                },
                ...
            ],
            'risk_level': str,
            'summary': str,
            'score': float
        }
    """
    try:
        # Load stock data
        stock_df = get_stock_data(stock_code)
        
        if len(stock_df) < 30:
            return {
                'stock_code': stock_code,
                'stock_name': get_stock_name(stock_code),
                'date': pd.Timestamp.now().strftime('%Y-%m-%d'),
                'anomalies_detected': [],
                'risk_level': 'NORMAL',
                'summary': 'Données insuffisantes pour l\'analyse d\'anomalies',
                'score': 0.0,
                'ml_enabled': False,
                'error': 'Insufficient data'
            }
        
        # Engineer features for ML detection
        try:
            stock_df = engineer_features(stock_df)
        except Exception as e:
            print(f"Warning: Feature engineering failed ({e}), using basic features")
            use_ml = False
        
        # Get recent data
        recent_df = stock_df.tail(lookback_days).copy()
        
        # ML-based detection
        ml_anomalies = set()
        if use_ml:
            try:
                model = load_model()
                if model:
                    recent_with_predictions = model.predict(recent_df)
                    ml_detected = recent_with_predictions[
                        recent_with_predictions['anomaly_label'] == -1
                    ]
                    ml_anomalies = set(ml_detected['date'].dt.strftime('%Y-%m-%d'))
                else:
                    use_ml = False
            except Exception as e:
                print(f"Warning: ML detection failed ({e}), using statistical methods only")
                use_ml = False
        
        # Run all statistical detection algorithms
        all_anomalies = []
        
        # Enhanced row-based detection (from Module3)
        for idx, row in recent_df.iterrows():
            # Volume spike
            vol_anomaly = detect_volume_spike(row, threshold_sigma=2.5)
            if vol_anomaly:
                all_anomalies.append(vol_anomaly)

            # Price gap
            price_anomaly = detect_price_gap(row, threshold_pct=0.03, threshold_sigma=2.0)
            if price_anomaly:
                all_anomalies.append(price_anomaly)

            # Low liquidity
            liquidity_anomaly = detect_low_liquidity(row, threshold_transactions=3)
            if liquidity_anomaly and liquidity_anomaly['severity'] == 'HIGH':
                all_anomalies.append(liquidity_anomaly)

            # Price-volume divergence
            divergence = detect_price_volume_divergence(row)
            if divergence:
                all_anomalies.append(divergence)

            # If ML flagged this date but statistical didn't, add ML anomaly
            date_str = row['date'].strftime('%Y-%m-%d')
            if use_ml and date_str in ml_anomalies:
                if not any(a['date'] == date_str for a in all_anomalies):
                    all_anomalies.append({
                        'type': 'ml_detected',
                        'severity': 'MEDIUM',
                        'date': date_str,
                        'description': f"Modèle ML a détecté un comportement atypique",
                        'metrics': {
                            'volume': float(row['volume']),
                            'price_change': float(row.get('price_change_pct', 0))
                        }
                    })
        
        # Assign unique alert IDs
        timestamp_base = datetime.now().strftime('%Y%m%d%H%M%S%f')
        for idx, anom in enumerate(all_anomalies):
            anom['alert_id'] = f"{timestamp_base}_{stock_code}_{idx}"
            anom['timestamp'] = datetime.now().isoformat()

        # Calculate overall score
        score = calculate_anomaly_score(all_anomalies)
        risk_level = determine_risk_level(score)
        
        # Generate summary
        if not all_anomalies:
            summary = "Aucune anomalie significative détectée. Comportement normal du marché."
        else:
            anom_counts = {}
            for anom in all_anomalies:
                anom_type = anom['type']
                anom_counts[anom_type] = anom_counts.get(anom_type, 0) + 1
            
            summary_parts = []
            type_names = {
                'volume_spike': 'spike(s) de volume',
                'price_gap': 'gap(s) de prix',
                'low_liquidity': 'événement(s) de faible liquidité',
                'high_volatility': 'période(s) de forte volatilité'
            }
            
            for atype, count in anom_counts.items():
                summary_parts.append(f"{count} {type_names.get(atype, atype)}")
            
            summary = f"Anomalies détectées: {', '.join(summary_parts)}. Niveau de risque: {risk_level}."
        
        # Sort anomalies by date (most recent first) and severity
        severity_order = {'HIGH': 0, 'MEDIUM': 1, 'LOW': 2}
        all_anomalies.sort(key=lambda x: (x['date'], severity_order.get(x['severity'], 3)), reverse=True)

        # Register alerts with AlertManager
        try:
            manager = get_default_alert_manager()
            for anom in all_anomalies:
                manager.register_alert({
                    'alert_id': anom.get('alert_id'),
                    'stock_code': stock_code,
                    'stock_name': get_stock_name(stock_code),
                    'type': anom.get('type'),
                    'severity': anom.get('severity'),
                    'date': anom.get('date'),
                    'timestamp': anom.get('timestamp'),
                    'description': anom.get('description'),
                    'metrics': anom.get('metrics', {}),
                })
        except Exception:
            pass
        
        return {
            'stock_code': stock_code,
            'stock_name': get_stock_name(stock_code),
            'date': stock_df['date'].iloc[-1].strftime('%Y-%m-%d'),
            'anomalies_detected': all_anomalies,
            'risk_level': risk_level,
            'summary': summary,
            'score': float(score),
            'ml_enabled': use_ml
        }
    
    except Exception as e:
        return {
            'stock_code': stock_code,
            'stock_name': get_stock_name(stock_code),
            'date': pd.Timestamp.now().strftime('%Y-%m-%d'),
            'anomalies_detected': [],
            'risk_level': 'NORMAL',
            'summary': f'Erreur lors de l\'analyse: {str(e)}',
            'score': 0.0,
            'ml_enabled': False,
            'error': str(e)
        }


# Testing
if __name__ == "__main__":
    print("Testing anomaly detection module...")
    
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
            result = detect_anomalies(stock_code, lookback_days=30)
            
            print(f"\nAnomaly Score: {result['score']:.1f}/10")
            print(f"Risk Level: {result['risk_level']}")
            print(f"Summary: {result['summary']}")
            
            if result['anomalies_detected']:
                print(f"\nDetailed Anomalies ({len(result['anomalies_detected'])} found):")
                
                for anom in result['anomalies_detected'][:5]:  # Show first 5
                    print(f"\n  [{anom['severity']}] {anom['type']} on {anom['date']}")
                    print(f"  {anom['description']}")
                
                if len(result['anomalies_detected']) > 5:
                    print(f"\n  ... and {len(result['anomalies_detected']) - 5} more")
            else:
                print("\n✅ No anomalies detected - normal market behavior")
        
        except Exception as e:
            print(f"  Error: {e}")
    
    print("\n✅ Anomaly detection module test complete!")
