"""
Decision Engine
================
The core integration point for the Intelligent Trading Assistant.
Combines signals from forecasting, sentiment, and anomaly detection
to produce actionable trading recommendations.
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime

# Toggle between mocks and real modules
USE_MOCKS = False  # ✅ ENHANCED: Now using real modules!

if USE_MOCKS:
    from .mocks import (
        get_forecast_mock as get_forecast,
        get_sentiment_mock as get_sentiment,
        get_anomalies_mock as get_anomalies,
        get_current_price_mock as get_current_price,
        get_stock_name_mock as get_stock_name,
        get_all_stock_codes_mock as get_all_stock_codes,
    )
else:
    # Real imports - ✅ INTEGRATED
    from .stock_data import (
        get_current_price,
        get_stock_name,
        get_all_stock_codes,
        calculate_rsi,
        get_volatility,
    )
    from modules.forecasting.predict import predict_next_days
    from modules.sentiment.analyzer import get_sentiment_score
    from modules.anomaly.detector import detect_anomalies

from .explainer import generate_explanation, generate_short_explanation
from .technical_indicators import calculate_rsi, calculate_macd


# ============================================================================
# CONFIGURATION
# ============================================================================

# Signal weights (must sum to ~1.0)
WEIGHTS = {
    'forecast': 0.40,    # Rania's module
    'sentiment': 0.30,   # Chiraz's module
    'anomaly': 0.20,     # Malek's module
    'technical': 0.10,   # RSI (optional)
}

# Thresholds for recommendations
THRESHOLDS = {
    'buy': 3.0,          # Score >= 3 -> BUY
    'sell': -3.0,        # Score <= -3 -> SELL
    'strong_signal': 5.0  # For high confidence
}

# User profile adjustments
PROFILE_MULTIPLIERS = {
    'conservative': 0.5,   # Dampen weak signals
    'moderate': 1.0,       # No adjustment
    'aggressive': 1.2,     # Amplify signals
}


# ============================================================================
# MAIN RECOMMENDATION FUNCTION
# ============================================================================

def make_recommendation(stock_code: str, user_profile: str = 'moderate') -> dict:
    """
    Combines all signals and returns a trading recommendation.

    Args:
        stock_code: ISIN code like 'TN0001600154'
        user_profile: 'conservative' | 'moderate' | 'aggressive'

    Returns:
        {
            'stock_code': str,
            'stock_name': str,
            'recommendation': str,  # 'BUY' | 'SELL' | 'HOLD'
            'confidence': float,    # 0 to 1
            'score': float,         # Internal score (for debugging)
            'explanation': str,     # Human-readable explanation
            'signals': {...},       # Individual signal details
            'risk_level': str,      # 'LOW' | 'MEDIUM' | 'HIGH'
            'suggested_action': str,
            'timestamp': str
        }
    """
    # Get stock info
    stock_name = get_stock_name(stock_code)
    current_price = get_current_price(stock_code)

    # Calculate decision score
    score, signals, explanations = _calculate_decision_score(stock_code)

    # Apply user profile adjustment
    profile_mult = PROFILE_MULTIPLIERS.get(user_profile, 1.0)
    adjusted_score = score * profile_mult

    # Convert score to recommendation
    recommendation, confidence = _score_to_recommendation(adjusted_score, user_profile)

    # Assess risk level
    risk_level = _assess_risk(signals, score)

    # Generate suggested action
    suggested_action = _generate_suggested_action(
        recommendation, stock_name, current_price, confidence, user_profile
    )

    # Build result
    result = {
        'stock_code': stock_code,
        'stock_name': stock_name,
        'current_price': current_price,
        'recommendation': recommendation,
        'confidence': confidence,
        'score': round(adjusted_score, 2),
        'raw_score': round(score, 2),
        'signals': signals,
        'risk_level': risk_level,
        'suggested_action': suggested_action,
        'user_profile': user_profile,
        'timestamp': datetime.now().isoformat(),
    }

    # Add full explanation
    result['explanation'] = generate_explanation(result)
    result['short_explanation'] = generate_short_explanation(result)

    return result


def _calculate_decision_score(stock_code: str) -> Tuple[float, Dict, List[str]]:
    """
    Aggregates all signals into a single score.

    Score range: -10 to +10
    - Positive score -> BUY
    - Negative score -> SELL
    - Near zero -> HOLD

    Returns:
        (score, signals_dict, explanations_list)
    """
    score = 0.0
    explanations = []
    signals = {}

    # ========================================================================
    # SIGNAL 1: FORECASTING (40% weight)
    # ========================================================================
    try:
        forecast = get_forecast(stock_code)
        trend = forecast.get('trend', 0)
        forecast_confidence = forecast.get('confidence', 0.5)

        if trend > 0.02:  # >2% predicted growth
            points = min(trend * 100, 4)  # max 4 points
            score += points
            direction = 'up'
            explanations.append(
                f"Prevision positive: +{trend:.1%} attendu sur 5 jours"
            )
        elif trend < -0.02:  # >2% predicted decline
            points = max(trend * 100, -4)  # min -4 points
            score += points
            direction = 'down'
            explanations.append(
                f"Prevision negative: {trend:.1%} attendu sur 5 jours"
            )
        else:
            direction = 'stable'
            explanations.append("Prevision stable, pas de tendance claire")

        signals['forecast'] = {
            'direction': direction,
            'magnitude': abs(trend),
            'confidence': forecast_confidence,
            'weight': WEIGHTS['forecast'],
            'predictions': forecast.get('predictions', [])
        }

    except Exception as e:
        signals['forecast'] = {'error': str(e), 'direction': 'unknown', 'magnitude': 0}
        explanations.append("Prevision non disponible")

    # ========================================================================
    # SIGNAL 2: SENTIMENT ANALYSIS (30% weight)
    # ========================================================================
    try:
        sentiment = get_sentiment(stock_code)
        sent_score = sentiment.get('score', 0)
        num_articles = sentiment.get('num_articles', 0)

        if sent_score > 0.4:
            points = sent_score * 3  # max ~3 points
            score += points
            explanations.append(
                f"Sentiment positif ({sent_score:.2f}) base sur {num_articles} articles"
            )
        elif sent_score < -0.4:
            points = sent_score * 3  # min ~-3 points
            score += points
            explanations.append(
                f"Sentiment negatif ({sent_score:.2f}) - prudence recommandee"
            )
        elif num_articles > 0:
            explanations.append(
                f"Sentiment neutre ({sent_score:.2f}) - marche indecis"
            )
        else:
            explanations.append("Pas d'articles recents pour l'analyse de sentiment")

        signals['sentiment'] = {
            'score': sent_score,
            'num_articles': num_articles,
            'headlines': sentiment.get('sample_headlines', []),
            'weight': WEIGHTS['sentiment']
        }

    except Exception as e:
        signals['sentiment'] = {'error': str(e), 'score': 0}
        explanations.append("Analyse de sentiment non disponible")

    # ========================================================================
    # SIGNAL 3: ANOMALY DETECTION (20% weight)
    # ========================================================================
    try:
        anomalies = get_anomalies(stock_code)
        has_anomaly = anomalies.get('any_anomaly', False)
        anomaly_score = anomalies.get('anomaly_score', 0)

        if anomalies.get('volume_spike', False):
            score -= 2  # Suspicious activity
            explanations.append(
                "Pic de volume anormal detecte - possible manipulation"
            )

        if anomalies.get('price_spike', False):
            score -= 1
            explanations.append(
                "Variation de prix inhabituelle sans actualite justificative"
            )

        if not has_anomaly:
            score += 1  # Normal trading is a positive signal
            explanations.append("Aucune anomalie detectee - trading normal")

        signals['anomaly'] = {
            'detected': has_anomaly,
            'volume_spike': anomalies.get('volume_spike', False),
            'price_spike': anomalies.get('price_spike', False),
            'anomaly_score': anomaly_score,
            'details': anomalies.get('details', ''),
            'weight': WEIGHTS['anomaly']
        }

    except Exception as e:
        signals['anomaly'] = {'error': str(e), 'detected': False}
        explanations.append("Detection d'anomalies non disponible")

    # ========================================================================
    # SIGNAL 4: TECHNICAL INDICATORS (10% weight) - Optional
    # ========================================================================
    try:
        from .stock_data import get_stock_data

        history = get_stock_data(stock_code)
        if 'close' not in history.columns and 'CLOTURE' in history.columns:
            history = history.rename(columns={'CLOTURE': 'close'})

        rsi = calculate_rsi(history)
        macd = calculate_macd(history)

        rsi_signal = 'neutral'
        macd_trend = macd.get('trend') if macd else None

        if rsi is not None:
            if rsi < 30:
                score += 1.5
                rsi_signal = 'oversold'
                explanations.append(
                    f"RSI indique survente ({rsi:.1f}) - opportunite d'achat"
                )
            elif rsi > 70:
                score -= 1.5
                rsi_signal = 'overbought'
                explanations.append(
                    f"RSI indique surachat ({rsi:.1f}) - risque de correction"
                )

        if macd_trend == 'bullish':
            score += 0.5
            explanations.append("MACD confirme tendance haussiere")
        elif macd_trend == 'bearish':
            score -= 0.5
            explanations.append("MACD indique tendance baissiere")

        if rsi is not None or macd is not None:
            signals['technical'] = {
                'rsi': rsi if rsi is not None else None,
                'macd': macd if macd is not None else None,
                'signal': macd_trend if macd_trend else rsi_signal,
                'weight': WEIGHTS['technical']
            }

    except Exception as e:
        signals['technical'] = {'error': str(e)}

    # ========================================================================
    # SIGNAL 5: MARKET MEMORY (Semantic Evidence) - Optional
    # ========================================================================
    try:
        from modules.memory.qdrant_store import QdrantStore
        from modules.memory.embeddings import get_embedding_provider
        
        store = QdrantStore()
        if store.is_available():
            embedder = get_embedding_provider()
            query_text = f"{get_stock_name(stock_code)} {stock_code} analyse"
            
            # Search each collection
            memory_evidence = {}
            for collection in ['bvmt_news', 'bvmt_anomalies', 'bvmt_recommendations']:
                query_vector = embedder.embed_query(query_text)
                results = store.search(
                    collection_name=collection,
                    query_vector=query_vector,
                    top_k=3,
                    score_threshold=0.3,
                    filters={'ticker': stock_code}
                )
                key = collection.replace('bvmt_', '')
                memory_evidence[key] = results
            
            signals['memory'] = memory_evidence
            
            # Count total evidence
            total_evidence = sum(len(items) for items in memory_evidence.values())
            if total_evidence > 0:
                explanations.append(
                    f"Evidence semantique: {total_evidence} elements retrouves dans Market Memory"
                )
    except Exception as e:
        # Market memory is optional - fail gracefully
        signals['memory'] = {}
        pass

    return score, signals, explanations


def _score_to_recommendation(score: float, user_profile: str) -> Tuple[str, float]:
    """Convert numeric score to recommendation and confidence"""

    if user_profile == 'conservative':
        # Conservative users need stronger signals
        buy_threshold = 4.0
        sell_threshold = -4.0
    elif user_profile == 'aggressive':
        # Aggressive users act on weaker signals
        buy_threshold = 2.0
        sell_threshold = -2.0
    else:
        buy_threshold = THRESHOLDS['buy']
        sell_threshold = THRESHOLDS['sell']

    if score >= buy_threshold:
        recommendation = 'BUY'
        # Confidence scales with score strength
        confidence = min(0.5 + (score - buy_threshold) * 0.1, 0.95)
    elif score <= sell_threshold:
        recommendation = 'SELL'
        confidence = min(0.5 + (abs(score) - abs(sell_threshold)) * 0.1, 0.95)
    else:
        recommendation = 'HOLD'
        # Lower confidence for HOLD - indicates uncertainty
        confidence = 0.5 + abs(score) * 0.05

    return recommendation, round(confidence, 2)


def _assess_risk(signals: Dict, score: float) -> str:
    """Assess overall risk level based on signals"""

    risk_score = 0

    # Anomalies increase risk
    anomaly = signals.get('anomaly', {})
    if anomaly.get('detected', False):
        risk_score += 2
    if anomaly.get('anomaly_score', 0) > 0.7:
        risk_score += 1

    # Low forecast confidence increases risk
    forecast = signals.get('forecast', {})
    if forecast.get('confidence', 1) < 0.5:
        risk_score += 1

    # Extreme sentiment can indicate risk
    sentiment = signals.get('sentiment', {})
    if abs(sentiment.get('score', 0)) > 0.8:
        risk_score += 1

    # Technical extremes
    technical = signals.get('technical', {})
    rsi = technical.get('rsi', 50)
    if rsi and (rsi < 20 or rsi > 80):
        risk_score += 1

    # Very strong scores might indicate higher risk (volatile situation)
    if abs(score) > 7:
        risk_score += 1

    if risk_score <= 1:
        return 'LOW'
    elif risk_score <= 3:
        return 'MEDIUM'
    else:
        return 'HIGH'


def _generate_suggested_action(
    recommendation: str,
    stock_name: str,
    current_price: float,
    confidence: float,
    user_profile: str
) -> str:
    """Generate a concrete suggested action"""

    # Suggest quantity based on profile
    if user_profile == 'conservative':
        qty_range = "20-50"
        action_modifier = "prudemment"
    elif user_profile == 'aggressive':
        qty_range = "100-200"
        action_modifier = ""
    else:
        qty_range = "50-100"
        action_modifier = ""

    if recommendation == 'BUY':
        if confidence >= 0.7:
            return f"Acheter {action_modifier} {qty_range} actions de {stock_name} au prix actuel de {current_price:.2f} TND"
        else:
            return f"Envisager l'achat de {qty_range} actions - surveiller le prix avant d'agir"

    elif recommendation == 'SELL':
        if confidence >= 0.7:
            return f"Vendre {action_modifier} vos positions sur {stock_name} au prix de {current_price:.2f} TND"
        else:
            return f"Envisager de reduire votre position - placer un ordre stop-loss"

    else:
        return f"Conserver votre position actuelle sur {stock_name} - pas d'action immediate"


# ============================================================================
# BATCH ANALYSIS FUNCTIONS
# ============================================================================

def get_top_recommendations(
    n: int = 5,
    user_profile: str = 'moderate',
    recommendation_type: str = 'all'
) -> List[Dict]:
    """
    Get top N recommendations across all stocks.

    Args:
        n: Number of recommendations to return
        user_profile: User risk profile
        recommendation_type: 'buy', 'sell', 'all'

    Returns:
        List of recommendation dicts, sorted by score strength
    """
    all_recommendations = []
    stock_codes = get_all_stock_codes()

    for code in stock_codes:
        try:
            rec = make_recommendation(code, user_profile)
            all_recommendations.append(rec)
        except Exception as e:
            print(f"Error analyzing {code}: {e}")
            continue

    # Filter by type if specified
    if recommendation_type == 'buy':
        all_recommendations = [r for r in all_recommendations if r['recommendation'] == 'BUY']
    elif recommendation_type == 'sell':
        all_recommendations = [r for r in all_recommendations if r['recommendation'] == 'SELL']

    # Sort by absolute score (strongest signals first)
    all_recommendations.sort(key=lambda x: abs(x['score']), reverse=True)

    return all_recommendations[:n]


def analyze_portfolio_stocks(stock_codes: List[str], user_profile: str = 'moderate') -> List[Dict]:
    """
    Analyze a list of stocks (e.g., user's current holdings).

    Returns recommendations for each stock in the portfolio.
    """
    results = []
    for code in stock_codes:
        try:
            rec = make_recommendation(code, user_profile)
            results.append(rec)
        except Exception as e:
            results.append({
                'stock_code': code,
                'error': str(e),
                'recommendation': 'HOLD',
                'confidence': 0,
                'explanation': 'Erreur lors de l\'analyse'
            })
    return results


def get_market_summary(user_profile: str = 'moderate') -> Dict:
    """
    Generate an overall market summary.

    Returns:
        {
            'overall_sentiment': str,
            'buy_signals': int,
            'sell_signals': int,
            'hold_signals': int,
            'top_buys': List[Dict],
            'top_sells': List[Dict],
            'alerts': List[str]
        }
    """
    stock_codes = get_all_stock_codes()
    all_recs = []

    for code in stock_codes:
        try:
            rec = make_recommendation(code, user_profile)
            all_recs.append(rec)
        except:
            continue

    buy_count = sum(1 for r in all_recs if r['recommendation'] == 'BUY')
    sell_count = sum(1 for r in all_recs if r['recommendation'] == 'SELL')
    hold_count = sum(1 for r in all_recs if r['recommendation'] == 'HOLD')

    # Overall sentiment
    if buy_count > sell_count * 1.5:
        overall = 'HAUSSIER'
    elif sell_count > buy_count * 1.5:
        overall = 'BAISSIER'
    else:
        overall = 'NEUTRE'

    # Get top buys and sells
    buys = sorted([r for r in all_recs if r['recommendation'] == 'BUY'],
                  key=lambda x: x['score'], reverse=True)[:5]
    sells = sorted([r for r in all_recs if r['recommendation'] == 'SELL'],
                   key=lambda x: x['score'])[:5]

    # Generate alerts
    alerts = []
    for rec in all_recs:
        if rec['signals'].get('anomaly', {}).get('detected', False):
            alerts.append(f"Anomalie detectee sur {rec['stock_name']}")
        if rec['confidence'] >= 0.8:
            alerts.append(f"Signal fort: {rec['recommendation']} {rec['stock_name']}")

    return {
        'overall_sentiment': overall,
        'buy_signals': buy_count,
        'sell_signals': sell_count,
        'hold_signals': hold_count,
        'total_analyzed': len(all_recs),
        'top_buys': buys,
        'top_sells': sells,
        'alerts': alerts[:10],  # Limit to 10 alerts
        'timestamp': datetime.now().isoformat()
    }


# ============================================================================
# INTEGRATION HELPERS (for Phase 2)
# ============================================================================

def get_forecast_wrapper(stock_code: str) -> dict:
    """
    Wrapper for forecasting module.
    Normalizes output format and handles errors.
    ✅ ENHANCED: Now using real predict_next_days module
    """
    try:
        if USE_MOCKS:
            result = get_forecast(stock_code)
        else:
            # ✅ Use real forecasting module
            result = predict_next_days(stock_code, n_days=5)

        # Normalize output
        if 'predictions' in result:
            predictions = result['predictions']
            if len(predictions) >= 2:
                first_price = predictions[0] if isinstance(predictions[0], (int, float)) else predictions[0].get('predicted_close', predictions[0].get('close', 0))
                last_price = predictions[-1] if isinstance(predictions[-1], (int, float)) else predictions[-1].get('predicted_close', predictions[-1].get('close', 0))
                if first_price > 0:
                    trend = (last_price - first_price) / first_price
                else:
                    trend = 0
            else:
                trend = result.get('trend', 0)
        else:
            trend = result.get('trend', 0)

        return {
            'trend': trend,
            'confidence': result.get('confidence', result.get('metrics', {}).get('directional_accuracy', 0.5)),
            'predictions': result.get('predictions', [])
        }

    except Exception as e:
        print(f"Forecast error for {stock_code}: {e}")
        return {'trend': 0, 'confidence': 0, 'error': str(e)}


def get_sentiment_wrapper(stock_code: str) -> dict:
    """
    Wrapper for sentiment analysis module.
    ✅ ENHANCED: Now using real sentiment with advanced ML support
    """
    try:
        if USE_MOCKS:
            result = get_sentiment(stock_code)
        else:
            # ✅ Use real sentiment module with advanced analysis
            # Try advanced analysis first (with keyword fallback)
            result = get_sentiment_score(
                stock_code, 
                use_advanced=True,  # Enable ML analysis
                provider="auto"     # Auto-select best method
            )

        return {
            'score': result.get('sentiment_score', result.get('score', 0)),
            'num_articles': result.get('num_articles', 0),
            'sample_headlines': result.get('sample_headlines', []),
            'method': result.get('method', 'unknown'),
            'correction_applied': result.get('correction_applied', False)
        }

    except Exception as e:
        print(f"Sentiment error for {stock_code}: {e}")
        return {'score': 0, 'num_articles': 0, 'error': str(e)}


def get_anomalies_wrapper(stock_code: str) -> dict:
    """
    Wrapper for anomaly detection module.
    ✅ ENHANCED: Now using real anomaly detector with ML
    """
    try:
        if USE_MOCKS:
            result = get_anomalies(stock_code)
        else:
            # ✅ Use real anomaly detection module
            result = detect_anomalies(stock_code, lookback_days=30)

        # Normalize output
        anomalies_list = result.get('anomalies_detected', [])
        has_anomaly = len(anomalies_list) > 0
        
        # Check for specific anomaly types
        volume_spike = any(a.get('type') == 'volume_spike' for a in anomalies_list)
        price_spike = any(a.get('type') in ['price_gap', 'price_volatility'] for a in anomalies_list)
        
        return {
            'volume_spike': volume_spike,
            'price_spike': price_spike,
            'any_anomaly': has_anomaly,
            'anomaly_score': result.get('score', 0),
            'risk_level': result.get('risk_level', 'NORMAL'),
            'details': result.get('summary', ''),
            'anomalies_detected': anomalies_list
        }

    except Exception as e:
        print(f"Anomaly detection error for {stock_code}: {e}")
        return {'any_anomaly': False, 'anomaly_score': 0, 'error': str(e)}
