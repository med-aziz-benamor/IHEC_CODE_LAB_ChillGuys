"""
Explainability System
======================
Converts technical signals into human-readable explanations.
This is MANDATORY for the jury - it's what makes the system special.
"""

from typing import Dict, Optional


def generate_explanation(recommendation_data: dict, language: str = 'fr') -> str:
    """
    Convert technical signals into plain language explanation.

    Args:
        recommendation_data: Output from make_recommendation()
        language: 'fr' for French, 'en' for English

    Returns:
        Human-readable explanation string
    """
    if language == 'fr':
        return _generate_french_explanation(recommendation_data)
    else:
        return _generate_english_explanation(recommendation_data)


def _generate_french_explanation(data: dict) -> str:
    """Generate French explanation (primary for Tunisian market)"""

    rec = data.get('recommendation', 'HOLD')
    stock_name = data.get('stock_name', data.get('stock_code', 'Cette action'))
    confidence = data.get('confidence', 0.5)
    signals = data.get('signals', {})
    risk = data.get('risk_level', 'MEDIUM')

    # Recommendation header
    if rec == 'BUY':
        header = f"RECOMMANDATION: ACHETER {stock_name}"
        action_verb = "d'ACHETER"
        color_hint = "(Signal positif)"
    elif rec == 'SELL':
        header = f"RECOMMANDATION: VENDRE {stock_name}"
        action_verb = "de VENDRE"
        color_hint = "(Signal negatif)"
    else:
        header = f"RECOMMANDATION: CONSERVER {stock_name}"
        action_verb = "de CONSERVER"
        color_hint = "(Signal neutre)"

    # Build explanation
    lines = [
        header,
        f"Confiance: {confidence:.0%} {color_hint}",
        "",
        "ANALYSE DETAILLEE:",
        "-" * 40,
    ]

    # Forecast signal
    forecast = signals.get('forecast', {})
    if forecast:
        direction = forecast.get('direction', 'stable')
        magnitude = forecast.get('magnitude', 0)

        if direction == 'up':
            lines.append(f"  Prevision: Hausse attendue de +{magnitude:.1%} sur 5 jours")
            lines.append(f"            Le modele de prediction indique une tendance haussiere")
        elif direction == 'down':
            lines.append(f"  Prevision: Baisse attendue de {magnitude:.1%} sur 5 jours")
            lines.append(f"            Le modele de prediction indique une tendance baissiere")
        else:
            lines.append(f"  Prevision: Tendance stable, pas de mouvement significatif attendu")

    lines.append("")

    # Sentiment signal
    sentiment = signals.get('sentiment', {})
    if sentiment:
        score = sentiment.get('score', 0)
        num_articles = sentiment.get('num_articles', 0)

        if score > 0.3:
            sentiment_text = "positif"
            emoji = "(+)"
        elif score < -0.3:
            sentiment_text = "negatif"
            emoji = "(-)"
        else:
            sentiment_text = "neutre"
            emoji = "(=)"

        lines.append(f"  Sentiment: {sentiment_text.upper()} {emoji}")
        lines.append(f"            Score: {score:.2f}/1.0 base sur {num_articles} articles recents")

    lines.append("")

    # Anomaly signal
    anomaly = signals.get('anomaly', {})
    if anomaly:
        detected = anomaly.get('detected', False)
        details = anomaly.get('details', '')

        if detected:
            lines.append(f"  Anomalies: DETECTEES (!)")
            lines.append(f"            {details}")
            lines.append(f"            Prudence recommandee - activite inhabituelle")
        else:
            lines.append(f"  Anomalies: Aucune detectee")
            lines.append(f"            Trading normal, pas de comportement suspect")

    lines.append("")

    # Technical indicators (if present)
    technical = signals.get('technical', {})
    if technical and 'rsi' in technical:
        rsi = technical['rsi']
        if rsi < 30:
            rsi_text = "SURVENTE (opportunite d'achat potentielle)"
        elif rsi > 70:
            rsi_text = "SURACHAT (risque de correction)"
        else:
            rsi_text = "zone neutre"
        lines.append(f"  RSI: {rsi:.1f} - {rsi_text}")
        lines.append("")

    # Market Memory Evidence (NEW)
    memory_evidence = signals.get('memory', {})
    if memory_evidence:
        lines.append("-" * 40)
        lines.append("EVIDENCE RETROUVEE (Market Memory):")
        lines.append("")
        
        evidence_count = 0
        for key in ['news', 'anomalies', 'recommendations']:
            items = memory_evidence.get(key, [])
            if items:
                evidence_count += len(items)
                for item in items[:2]:  # Show top 2 per category
                    text = item.get('text', '')
                    score = item.get('score', 0)
                    if key == 'news':
                        lines.append(f"  [Actualite] {text[:100]}... (Score: {score:.2f})")
                    elif key == 'anomalies':
                        lines.append(f"  [Anomalie] {text[:100]}... (Score: {score:.2f})")
                    elif key == 'recommendations':
                        lines.append(f"  [Recommandation] {text[:100]}... (Score: {score:.2f})")
        
        if evidence_count == 0:
            lines.append("  Aucune evidence semantique trouvee dans la memoire du marche")
        else:
            lines.append(f"")
            lines.append(f"  Total: {evidence_count} elements pertinents trouves")
        
        lines.append("")
    else:
        # Offline mode notice
        lines.append("-" * 40)
        lines.append("(Mode offline: memoire semantique indisponible)")
        lines.append("")

    # Risk assessment
    lines.append("-" * 40)
    risk_texts = {
        'LOW': 'FAIBLE - Volatilite reduite, investissement stable',
        'MEDIUM': 'MOYEN - Volatilite moderee, surveiller les positions',
        'HIGH': 'ELEVE - Forte volatilite, position speculative'
    }
    lines.append(f"NIVEAU DE RISQUE: {risk_texts.get(risk, 'Non evalue')}")

    lines.append("")

    # Suggested action
    suggested = data.get('suggested_action', '')
    if suggested:
        lines.append("-" * 40)
        lines.append(f"ACTION SUGGEREE: {suggested}")

    return '\n'.join(lines)


def _generate_english_explanation(data: dict) -> str:
    """Generate English explanation"""

    rec = data.get('recommendation', 'HOLD')
    stock_name = data.get('stock_name', data.get('stock_code', 'This stock'))
    confidence = data.get('confidence', 0.5)
    signals = data.get('signals', {})
    risk = data.get('risk_level', 'MEDIUM')

    # Recommendation header
    if rec == 'BUY':
        header = f"RECOMMENDATION: BUY {stock_name}"
    elif rec == 'SELL':
        header = f"RECOMMENDATION: SELL {stock_name}"
    else:
        header = f"RECOMMENDATION: HOLD {stock_name}"

    lines = [
        header,
        f"Confidence: {confidence:.0%}",
        "",
        "DETAILED ANALYSIS:",
        "-" * 40,
    ]

    # Forecast
    forecast = signals.get('forecast', {})
    if forecast:
        direction = forecast.get('direction', 'stable')
        magnitude = forecast.get('magnitude', 0)

        if direction == 'up':
            lines.append(f"  Forecast: Expected increase of +{magnitude:.1%} over 5 days")
        elif direction == 'down':
            lines.append(f"  Forecast: Expected decrease of {magnitude:.1%} over 5 days")
        else:
            lines.append(f"  Forecast: Stable trend, no significant movement expected")

    lines.append("")

    # Sentiment
    sentiment = signals.get('sentiment', {})
    if sentiment:
        score = sentiment.get('score', 0)
        num_articles = sentiment.get('num_articles', 0)

        if score > 0.3:
            sentiment_text = "POSITIVE"
        elif score < -0.3:
            sentiment_text = "NEGATIVE"
        else:
            sentiment_text = "NEUTRAL"

        lines.append(f"  Sentiment: {sentiment_text}")
        lines.append(f"            Score: {score:.2f}/1.0 based on {num_articles} recent articles")

    lines.append("")

    # Anomaly
    anomaly = signals.get('anomaly', {})
    if anomaly:
        detected = anomaly.get('detected', False)

        if detected:
            lines.append(f"  Anomalies: DETECTED - Unusual trading activity")
        else:
            lines.append(f"  Anomalies: None detected - Normal trading")

    lines.append("")

    # Risk
    lines.append("-" * 40)
    risk_texts = {
        'LOW': 'LOW - Low volatility, stable investment',
        'MEDIUM': 'MEDIUM - Moderate volatility, monitor positions',
        'HIGH': 'HIGH - High volatility, speculative position'
    }
    lines.append(f"RISK LEVEL: {risk_texts.get(risk, 'Not evaluated')}")

    # Suggested action
    suggested = data.get('suggested_action', '')
    if suggested:
        lines.append("")
        lines.append(f"SUGGESTED ACTION: {suggested}")

    return '\n'.join(lines)


def generate_short_explanation(recommendation_data: dict) -> str:
    """Generate a one-line summary for dashboards"""

    rec = recommendation_data.get('recommendation', 'HOLD')
    stock_name = recommendation_data.get('stock_name', '')
    confidence = recommendation_data.get('confidence', 0.5)

    if rec == 'BUY':
        return f"ACHETER {stock_name} (confiance: {confidence:.0%}) - Signaux positifs detectes"
    elif rec == 'SELL':
        return f"VENDRE {stock_name} (confiance: {confidence:.0%}) - Signaux negatifs detectes"
    else:
        return f"CONSERVER {stock_name} - Pas de signal fort, attendre"


def generate_alert_message(recommendation_data: dict) -> str:
    """Generate an alert message for notifications"""

    rec = recommendation_data.get('recommendation', 'HOLD')
    stock_name = recommendation_data.get('stock_name', '')
    confidence = recommendation_data.get('confidence', 0.5)
    signals = recommendation_data.get('signals', {})

    if rec == 'BUY' and confidence >= 0.7:
        return f"ALERTE ACHAT: {stock_name} presente une opportunite d'achat avec {confidence:.0%} de confiance"
    elif rec == 'SELL' and confidence >= 0.7:
        return f"ALERTE VENTE: {stock_name} montre des signaux de vente avec {confidence:.0%} de confiance"

    # Check for anomalies
    anomaly = signals.get('anomaly', {})
    if anomaly.get('detected', False):
        return f"ALERTE ANOMALIE: Activite inhabituelle detectee sur {stock_name}"

    return None


def format_signals_table(signals: dict) -> str:
    """Format signals as a readable table"""

    lines = [
        "| Signal      | Valeur    | Impact   |",
        "|-------------|-----------|----------|",
    ]

    # Forecast
    forecast = signals.get('forecast', {})
    if forecast:
        direction = forecast.get('direction', 'stable')
        magnitude = forecast.get('magnitude', 0)
        impact = '+' if direction == 'up' else ('-' if direction == 'down' else '=')
        lines.append(f"| Prevision   | {magnitude:+.1%}     | {impact}        |")

    # Sentiment
    sentiment = signals.get('sentiment', {})
    if sentiment:
        score = sentiment.get('score', 0)
        impact = '+' if score > 0.3 else ('-' if score < -0.3 else '=')
        lines.append(f"| Sentiment   | {score:.2f}      | {impact}        |")

    # Anomaly
    anomaly = signals.get('anomaly', {})
    if anomaly:
        detected = 'Oui' if anomaly.get('detected', False) else 'Non'
        impact = '-' if anomaly.get('detected', False) else '+'
        lines.append(f"| Anomalie    | {detected}       | {impact}        |")

    # Technical
    technical = signals.get('technical', {})
    if technical and 'rsi' in technical:
        rsi = technical['rsi']
        impact = '+' if rsi < 30 else ('-' if rsi > 70 else '=')
        lines.append(f"| RSI         | {rsi:.1f}      | {impact}        |")

    return '\n'.join(lines)
