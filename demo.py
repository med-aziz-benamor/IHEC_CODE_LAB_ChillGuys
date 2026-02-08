#!/usr/bin/env python3
"""
Intelligent Trading Assistant - Demo Script
============================================
IHEC CODELAB 2.0 Hackathon

This script demonstrates all the capabilities of the decision engine.
Use this to show the jury what your system can do.

Usage:
    python demo.py
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from modules.decision.engine import (
    make_recommendation,
    get_top_recommendations,
    get_market_summary,
)
from modules.decision.portfolio import Portfolio
from modules.decision.mocks import get_current_price_mock, get_all_stock_codes_mock


def print_header(title: str):
    """Print a styled header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def demo_single_stock_analysis():
    """Demonstrate analysis of a single stock"""
    print_header("ANALYSE D'UNE ACTION: ATTIJARI BANK (TN0001600154)")

    result = make_recommendation('TN0001600154', user_profile='moderate')

    # Print recommendation box
    rec = result['recommendation']
    if rec == 'BUY':
        box_char = '+'
        color_hint = "POSITIF"
    elif rec == 'SELL':
        box_char = '-'
        color_hint = "NEGATIF"
    else:
        box_char = '='
        color_hint = "NEUTRE"

    print(f"\n  {box_char * 50}")
    print(f"  {box_char}  RECOMMANDATION: {rec:^15}  ({color_hint})  {box_char}")
    print(f"  {box_char}  Confiance: {result['confidence']:.0%}               Score: {result['score']:+.1f}  {box_char}")
    print(f"  {box_char * 50}")

    print("\n" + result['explanation'])


def demo_market_overview():
    """Demonstrate market overview"""
    print_header("APERCU DU MARCHE BVMT")

    summary = get_market_summary()

    print(f"\n  Sentiment general: {summary['overall_sentiment']}")
    print(f"  Actions analysees: {summary['total_analyzed']}")
    print()
    print(f"  Signaux ACHAT:     {summary['buy_signals']} actions")
    print(f"  Signaux VENTE:     {summary['sell_signals']} actions")
    print(f"  Signaux CONSERVER: {summary['hold_signals']} actions")

    print("\n  TOP 5 OPPORTUNITES D'ACHAT:")
    print("  " + "-" * 50)
    for i, rec in enumerate(summary['top_buys'][:5], 1):
        print(f"  {i}. {rec['stock_name']:<20} Score: {rec['score']:+.2f}  "
              f"Conf: {rec['confidence']:.0%}")

    if summary['top_sells']:
        print("\n  ALERTES VENTE:")
        print("  " + "-" * 50)
        for i, rec in enumerate(summary['top_sells'][:3], 1):
            print(f"  {i}. {rec['stock_name']:<20} Score: {rec['score']:+.2f}")

    if summary['alerts']:
        print("\n  ALERTES:")
        for alert in summary['alerts'][:5]:
            print(f"  ! {alert}")


def demo_user_profiles():
    """Demonstrate different user profiles"""
    print_header("PROFILS D'INVESTISSEUR")

    stock_code = 'TN0001100254'  # SFBT

    print(f"\n  Analyse de SFBT pour differents profils:\n")

    profiles = [
        ('conservative', 'PRUDENT', 'Prefere la securite, accepte moins de risque'),
        ('moderate', 'MODERE', 'Equilibre entre risque et rendement'),
        ('aggressive', 'AGRESSIF', 'Maximise le rendement, accepte plus de risque'),
    ]

    for profile_id, profile_name, description in profiles:
        result = make_recommendation(stock_code, user_profile=profile_id)
        print(f"  [{profile_name}] {description}")
        print(f"      Recommandation: {result['recommendation']}")
        print(f"      Score: {result['score']:+.2f}, Confiance: {result['confidence']:.0%}")
        print()


def demo_portfolio_simulation():
    """Demonstrate portfolio management"""
    print_header("SIMULATION DE PORTEFEUILLE")

    # Create portfolio
    portfolio = Portfolio(initial_capital=10000, name="Demo Portfolio")
    print(f"\n  Capital initial: {portfolio.initial_capital:,.2f} TND")

    # Get top recommendations and buy them
    print("\n  Execution des meilleures recommandations...")
    print("  " + "-" * 50)

    buys = get_top_recommendations(n=4, recommendation_type='buy')
    current_prices = {}

    for rec in buys:
        price = get_current_price_mock(rec['stock_code'])
        current_prices[rec['stock_code']] = price
        quantity = int(2000 / price)  # ~2000 TND per position

        if quantity > 0 and portfolio.cash >= price * quantity:
            result = portfolio.buy(
                rec['stock_code'],
                rec['stock_name'],
                price=price,
                quantity=quantity,
                date='2026-02-07'
            )
            print(f"  ACHAT: {quantity} x {rec['stock_name']} @ {price:.2f} TND")

    # Show portfolio summary
    print("\n  " + "-" * 50)
    print("  RESUME DU PORTEFEUILLE:")
    print("  " + "-" * 50)

    metrics = portfolio.get_performance_metrics(current_prices)
    print(f"  Valeur totale:    {metrics['total_value']:>10,.2f} TND")
    print(f"  Cash disponible:  {metrics['cash']:>10,.2f} TND")
    print(f"  Valeur positions: {metrics['holdings_value']:>10,.2f} TND")
    print(f"  Nombre positions: {metrics['num_positions']:>10}")

    # Show positions
    print("\n  POSITIONS:")
    print("  " + "-" * 50)
    positions = portfolio.get_position_details(current_prices)
    for pos in positions:
        print(f"  {pos['stock_name']:<18} {pos['quantity']:>5} actions  "
              f"{pos['current_value']:>8,.2f} TND")

    # Show allocation
    print("\n  ALLOCATION:")
    allocation = portfolio.get_allocation(current_prices)
    for asset, pct in sorted(allocation.items(), key=lambda x: -x[1]):
        bar = "#" * int(pct / 2)
        print(f"  {asset:<18} {pct:>5.1f}% {bar}")


def demo_explainability():
    """Demonstrate the explainability feature"""
    print_header("SYSTEME D'EXPLICATION (FEATURE CLE)")

    print("""
  L'explicabilite est ce qui distingue notre systeme!

  Le jury apprecie particulierement:
  - Des explications claires en francais
  - La transparence des signaux utilises
  - Des suggestions d'action concretes
    """)

    result = make_recommendation('TN0001600154', user_profile='moderate')

    print("  EXPLICATION COMPLETE:")
    print("  " + "-" * 50)
    for line in result['explanation'].split('\n'):
        print(f"  {line}")

    print("\n  EXPLICATION COURTE (pour tableau de bord):")
    print(f"  >> {result['short_explanation']}")


def main():
    """Main demo function"""
    print("\n" + "#" * 70)
    print("#" + " " * 68 + "#")
    print("#    INTELLIGENT TRADING ASSISTANT - BVMT" + " " * 27 + "#")
    print("#    IHEC CODELAB 2.0 Hackathon" + " " * 37 + "#")
    print("#" + " " * 68 + "#")
    print("#" * 70)

    print("""
    Bienvenue dans la demonstration de notre Assistant de Trading Intelligent!

    Ce systeme combine:
    - Previsions de prix (Module Rania)
    - Analyse de sentiment (Module Chiraz)
    - Detection d'anomalies (Module Malek)
    - Moteur de decision avec explicabilite

    Appuyez sur Entree pour continuer...
    """)

    try:
        input()
    except:
        pass

    # Run all demos
    demo_single_stock_analysis()
    print("\n  [Appuyez sur Entree pour continuer...]")
    try:
        input()
    except:
        pass

    demo_market_overview()
    print("\n  [Appuyez sur Entree pour continuer...]")
    try:
        input()
    except:
        pass

    demo_user_profiles()
    print("\n  [Appuyez sur Entree pour continuer...]")
    try:
        input()
    except:
        pass

    demo_portfolio_simulation()
    print("\n  [Appuyez sur Entree pour continuer...]")
    try:
        input()
    except:
        pass

    demo_explainability()

    print_header("FIN DE LA DEMONSTRATION")
    print("""
    Notre systeme est pret pour:
    - Integration avec les modules des coequipiers
    - Construction du tableau de bord web
    - Backtesting sur donnees historiques 2022-2025

    Merci pour votre attention!
    """)


if __name__ == '__main__':
    main()
