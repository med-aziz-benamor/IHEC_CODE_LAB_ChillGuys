"""
Mock Data for Independent Development
======================================
Use these mocks during Phase 1 development.
Replace with real function calls in Phase 2.
"""

import random
from typing import Dict, List, Optional

# ============================================================================
# MOCK: FORECASTING MODULE (Rania's module)
# ============================================================================

def get_forecast_mock(stock_code: str) -> dict:
    """
    Simulates Rania's forecasting module.

    Returns predicted price trend for next 5 days.

    Returns:
        {
            'trend': float,        # Expected % change (-0.1 to 0.1)
            'confidence': float,   # Model confidence (0 to 1)
            'predictions': list    # Daily predicted prices
        }
    """
    # Predefined scenarios for demo stocks
    mock_forecasts = {
        # Strong upward trend - ATTIJARI BANK
        'TN0001600154': {
            'trend': 0.032,
            'confidence': 0.85,
            'predictions': [51.5, 52.0, 52.8, 53.2, 53.5]
        },
        # Slight downward trend - BIAT
        'TN0001800457': {
            'trend': -0.015,
            'confidence': 0.70,
            'predictions': [94.0, 93.5, 93.2, 92.8, 92.6]
        },
        # Neutral - TUNISAIR
        'TN0001900604': {
            'trend': 0.005,
            'confidence': 0.60,
            'predictions': [0.55, 0.55, 0.56, 0.55, 0.55]
        },
        # Strong upward - SFBT
        'TN0001100254': {
            'trend': 0.045,
            'confidence': 0.78,
            'predictions': [11.5, 11.8, 12.0, 12.2, 12.4]
        },
        # Moderate upward - BH
        'TN0001800853': {
            'trend': 0.025,
            'confidence': 0.72,
            'predictions': [10.5, 10.6, 10.7, 10.8, 10.9]
        },
        # Downward - STB
        'TN0003800200': {
            'trend': -0.028,
            'confidence': 0.65,
            'predictions': [5.2, 5.1, 5.0, 5.0, 4.9]
        },
        # Strong upward - POULINA
        'TN0006700406': {
            'trend': 0.038,
            'confidence': 0.80,
            'predictions': [12.0, 12.3, 12.5, 12.7, 12.9]
        },
        # Neutral - AMEN BANK
        'TN0003600154': {
            'trend': 0.008,
            'confidence': 0.55,
            'predictions': [38.0, 38.1, 38.2, 38.1, 38.3]
        },
    }

    if stock_code in mock_forecasts:
        return mock_forecasts[stock_code]

    # Generate random forecast for unknown stocks
    trend = random.uniform(-0.03, 0.03)
    return {
        'trend': trend,
        'confidence': random.uniform(0.4, 0.7),
        'predictions': [100 * (1 + trend * i/5) for i in range(5)]
    }


# ============================================================================
# MOCK: SENTIMENT MODULE (Chiraz's module)
# ============================================================================

def get_sentiment_mock(stock_code: str) -> dict:
    """
    Simulates Chiraz's sentiment analysis module.

    Returns sentiment score based on news/social media analysis.

    Returns:
        {
            'score': float,           # Sentiment score (-1 to 1)
            'num_articles': int,      # Number of articles analyzed
            'sample_headlines': list, # Sample headlines
            'sources': list           # Data sources used
        }
    """
    mock_sentiments = {
        # Positive sentiment - ATTIJARI BANK
        'TN0001600154': {
            'score': 0.65,
            'num_articles': 5,
            'sample_headlines': [
                'Attijari Bank annonce des resultats solides pour 2024',
                'La banque renforce sa presence digitale',
                'Nouvelle offre de credit pour les PME'
            ],
            'sources': ['Kapitalis', 'Webmanagercenter', 'L\'Economiste Maghrebin']
        },
        # Negative sentiment - BIAT
        'TN0001800457': {
            'score': -0.30,
            'num_articles': 3,
            'sample_headlines': [
                'Le secteur bancaire face a des defis de liquidite',
                'Incertitudes sur les marges bancaires'
            ],
            'sources': ['Business News', 'La Presse']
        },
        # Neutral - TUNISAIR
        'TN0001900604': {
            'score': 0.10,
            'num_articles': 4,
            'sample_headlines': [
                'Tunisair maintient ses operations normales',
                'Plan de restructuration en cours d\'evaluation'
            ],
            'sources': ['TAP', 'Tunisie Numerique']
        },
        # Very positive - SFBT
        'TN0001100254': {
            'score': 0.72,
            'num_articles': 6,
            'sample_headlines': [
                'SFBT: Hausse des ventes au T4 2024',
                'Le groupe diversifie ses activites',
                'Perspectives positives pour 2025'
            ],
            'sources': ['Bourse de Tunis', 'Ilboursa']
        },
        # Positive - POULINA
        'TN0006700406': {
            'score': 0.55,
            'num_articles': 4,
            'sample_headlines': [
                'Poulina Group: Expansion dans l\'agroalimentaire',
                'Resultats annuels superieurs aux attentes'
            ],
            'sources': ['Webmanagercenter', 'Kapitalis']
        },
        # Negative - STB
        'TN0003800200': {
            'score': -0.45,
            'num_articles': 3,
            'sample_headlines': [
                'STB: Les creances douteuses pesent sur les resultats',
                'Le secteur public bancaire sous pression'
            ],
            'sources': ['Business News', 'La Presse']
        },
    }

    if stock_code in mock_sentiments:
        return mock_sentiments[stock_code]

    # Generate neutral sentiment for unknown stocks
    return {
        'score': random.uniform(-0.2, 0.2),
        'num_articles': random.randint(0, 3),
        'sample_headlines': ['Pas d\'actualites recentes'],
        'sources': []
    }


# ============================================================================
# MOCK: ANOMALY DETECTION MODULE (Malek's module)
# ============================================================================

def get_anomalies_mock(stock_code: str) -> dict:
    """
    Simulates Malek's anomaly detection module.

    Detects unusual patterns in trading volume or price movements.

    Returns:
        {
            'volume_spike': bool,     # Unusual volume detected
            'price_spike': bool,      # Unusual price movement
            'any_anomaly': bool,      # Any anomaly detected
            'anomaly_score': float,   # Severity (0 to 1)
            'details': str            # Description of anomaly
        }
    """
    mock_anomalies = {
        # No anomalies - normal trading
        'TN0001600154': {
            'volume_spike': False,
            'price_spike': False,
            'any_anomaly': False,
            'anomaly_score': 0.1,
            'details': 'Trading normal, pas d\'anomalie detectee'
        },
        # Volume spike - BIAT
        'TN0001800457': {
            'volume_spike': True,
            'price_spike': False,
            'any_anomaly': True,
            'anomaly_score': 0.6,
            'details': 'Volume de transactions 3x superieur a la moyenne'
        },
        # Price spike - STB
        'TN0003800200': {
            'volume_spike': False,
            'price_spike': True,
            'any_anomaly': True,
            'anomaly_score': 0.5,
            'details': 'Variation de prix de 4% sans actualite justificative'
        },
        # Both anomalies - suspicious
        'TN0001900604': {
            'volume_spike': True,
            'price_spike': True,
            'any_anomaly': True,
            'anomaly_score': 0.85,
            'details': 'Activite suspecte: volume et prix anormaux simultanes'
        },
    }

    if stock_code in mock_anomalies:
        return mock_anomalies[stock_code]

    # Default: no anomalies
    return {
        'volume_spike': False,
        'price_spike': False,
        'any_anomaly': False,
        'anomaly_score': 0.05,
        'details': 'Trading normal'
    }


# ============================================================================
# MOCK: STOCK DATA (for testing without CSV files)
# ============================================================================

def get_current_price_mock(stock_code: str) -> float:
    """Returns mock current price for a stock"""
    mock_prices = {
        'TN0001600154': 51.50,   # ATTIJARI BANK
        'TN0001800457': 93.90,   # BIAT
        'TN0001900604': 0.55,    # TUNISAIR
        'TN0001100254': 11.53,   # SFBT
        'TN0001800853': 10.50,   # BH
        'TN0003800200': 5.20,    # STB
        'TN0006700406': 12.00,   # POULINA
        'TN0003600154': 38.00,   # AMEN BANK
        'TN0004900255': 25.50,   # UIB
        'TN0007100507': 15.80,   # DELICE HOLDING
    }
    return mock_prices.get(stock_code, 10.0)


def get_stock_name_mock(stock_code: str) -> str:
    """Returns mock stock name"""
    names = {
        'TN0001600154': 'ATTIJARI BANK',
        'TN0001800457': 'BIAT',
        'TN0001900604': 'TUNISAIR',
        'TN0001100254': 'SFBT',
        'TN0001800853': 'BH',
        'TN0003800200': 'STB',
        'TN0006700406': 'POULINA',
        'TN0003600154': 'AMEN BANK',
        'TN0004900255': 'UIB',
        'TN0007100507': 'DELICE HOLDING',
    }
    return names.get(stock_code, stock_code)


def get_all_stock_codes_mock() -> List[str]:
    """Returns list of mock stock codes for testing"""
    return [
        'TN0001600154',  # ATTIJARI BANK
        'TN0001800457',  # BIAT
        'TN0001900604',  # TUNISAIR
        'TN0001100254',  # SFBT
        'TN0001800853',  # BH
        'TN0003800200',  # STB
        'TN0006700406',  # POULINA
        'TN0003600154',  # AMEN BANK
    ]
