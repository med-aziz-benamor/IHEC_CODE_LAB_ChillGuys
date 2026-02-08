#!/usr/bin/env python3
"""
Trading Assistant REST API
===========================
Simple Flask API for dashboard integration.

Usage:
    pip install flask flask-cors
    python api.py

Endpoints:
    GET  /api/stocks              - List all stocks
    GET  /api/recommend/<code>    - Get recommendation for a stock
    GET  /api/market/summary      - Get market summary
    GET  /api/market/top-buys     - Get top buy recommendations
    GET  /api/market/top-sells    - Get top sell recommendations
    POST /api/portfolio/buy       - Execute buy order
    POST /api/portfolio/sell      - Execute sell order
    GET  /api/portfolio           - Get portfolio summary
    GET  /api/portfolio/positions - Get all positions
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
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
from modules.decision.mocks import (
    get_current_price_mock,
    get_stock_name_mock,
    get_all_stock_codes_mock
)

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend integration

# Global portfolio instance (in production, use a database)
portfolio = Portfolio(initial_capital=10000, name="Demo Portfolio")


# ============================================================================
# STOCK ENDPOINTS
# ============================================================================

@app.route('/api/stocks', methods=['GET'])
def list_stocks():
    """List all available stocks"""
    codes = get_all_stock_codes_mock()
    stocks = []
    for code in codes:
        stocks.append({
            'code': code,
            'name': get_stock_name_mock(code),
            'price': get_current_price_mock(code)
        })
    return jsonify({'stocks': stocks})


@app.route('/api/recommend/<stock_code>', methods=['GET'])
def get_recommendation(stock_code: str):
    """Get recommendation for a specific stock"""
    profile = request.args.get('profile', 'moderate')

    try:
        result = make_recommendation(stock_code, user_profile=profile)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/stock/<stock_code>', methods=['GET'])
def get_stock_info(stock_code: str):
    """Get basic stock information"""
    try:
        return jsonify({
            'code': stock_code,
            'name': get_stock_name_mock(stock_code),
            'price': get_current_price_mock(stock_code)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400


# ============================================================================
# MARKET ENDPOINTS
# ============================================================================

@app.route('/api/market/summary', methods=['GET'])
def market_summary():
    """Get overall market summary"""
    profile = request.args.get('profile', 'moderate')
    try:
        summary = get_market_summary(user_profile=profile)
        # Simplify for JSON serialization
        summary['top_buys'] = [
            {
                'stock_code': r['stock_code'],
                'stock_name': r['stock_name'],
                'recommendation': r['recommendation'],
                'confidence': r['confidence'],
                'score': r['score']
            }
            for r in summary['top_buys']
        ]
        summary['top_sells'] = [
            {
                'stock_code': r['stock_code'],
                'stock_name': r['stock_name'],
                'recommendation': r['recommendation'],
                'confidence': r['confidence'],
                'score': r['score']
            }
            for r in summary['top_sells']
        ]
        return jsonify(summary)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/market/top-buys', methods=['GET'])
def top_buys():
    """Get top buy recommendations"""
    n = request.args.get('n', 5, type=int)
    profile = request.args.get('profile', 'moderate')

    try:
        recommendations = get_top_recommendations(n=n, user_profile=profile, recommendation_type='buy')
        return jsonify({
            'count': len(recommendations),
            'recommendations': [
                {
                    'stock_code': r['stock_code'],
                    'stock_name': r['stock_name'],
                    'recommendation': r['recommendation'],
                    'confidence': r['confidence'],
                    'score': r['score'],
                    'short_explanation': r['short_explanation']
                }
                for r in recommendations
            ]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/market/top-sells', methods=['GET'])
def top_sells():
    """Get top sell recommendations"""
    n = request.args.get('n', 5, type=int)
    profile = request.args.get('profile', 'moderate')

    try:
        recommendations = get_top_recommendations(n=n, user_profile=profile, recommendation_type='sell')
        return jsonify({
            'count': len(recommendations),
            'recommendations': [
                {
                    'stock_code': r['stock_code'],
                    'stock_name': r['stock_name'],
                    'recommendation': r['recommendation'],
                    'confidence': r['confidence'],
                    'score': r['score'],
                    'short_explanation': r['short_explanation']
                }
                for r in recommendations
            ]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================================
# PORTFOLIO ENDPOINTS
# ============================================================================

@app.route('/api/portfolio', methods=['GET'])
def get_portfolio():
    """Get portfolio summary"""
    # Get current prices
    codes = list(portfolio.holdings.keys())
    current_prices = {code: get_current_price_mock(code) for code in codes}

    metrics = portfolio.get_performance_metrics(current_prices)
    allocation = portfolio.get_allocation(current_prices)

    return jsonify({
        'metrics': metrics,
        'allocation': allocation
    })


@app.route('/api/portfolio/positions', methods=['GET'])
def get_positions():
    """Get all portfolio positions"""
    codes = list(portfolio.holdings.keys())
    current_prices = {code: get_current_price_mock(code) for code in codes}

    positions = portfolio.get_position_details(current_prices)
    return jsonify({'positions': positions})


@app.route('/api/portfolio/transactions', methods=['GET'])
def get_transactions():
    """Get transaction history"""
    limit = request.args.get('limit', 20, type=int)
    history = portfolio.get_transaction_history(limit=limit)
    return jsonify({'transactions': history})


@app.route('/api/portfolio/buy', methods=['POST'])
def execute_buy():
    """Execute a buy order"""
    data = request.get_json()

    stock_code = data.get('stock_code')
    quantity = data.get('quantity', 0)

    if not stock_code:
        return jsonify({'error': 'stock_code is required'}), 400

    if quantity <= 0:
        return jsonify({'error': 'quantity must be positive'}), 400

    stock_name = get_stock_name_mock(stock_code)
    price = get_current_price_mock(stock_code)

    result = portfolio.buy(
        stock_code=stock_code,
        stock_name=stock_name,
        price=price,
        quantity=quantity
    )

    return jsonify(result)


@app.route('/api/portfolio/sell', methods=['POST'])
def execute_sell():
    """Execute a sell order"""
    data = request.get_json()

    stock_code = data.get('stock_code')
    quantity = data.get('quantity', 0)

    if not stock_code:
        return jsonify({'error': 'stock_code is required'}), 400

    if quantity <= 0:
        return jsonify({'error': 'quantity must be positive'}), 400

    price = get_current_price_mock(stock_code)

    result = portfolio.sell(
        stock_code=stock_code,
        price=price,
        quantity=quantity
    )

    return jsonify(result)


@app.route('/api/portfolio/reset', methods=['POST'])
def reset_portfolio():
    """Reset portfolio to initial state"""
    global portfolio
    initial_capital = request.get_json().get('initial_capital', 10000)
    portfolio = Portfolio(initial_capital=initial_capital, name="Demo Portfolio")
    return jsonify({'success': True, 'message': 'Portfolio reset', 'capital': initial_capital})


# ============================================================================
# HEALTH CHECK
# ============================================================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """API health check"""
    return jsonify({
        'status': 'healthy',
        'module': 'decision-engine',
        'version': '1.0.0'
    })


@app.route('/', methods=['GET'])
def index():
    """API documentation"""
    return jsonify({
        'name': 'Intelligent Trading Assistant API',
        'version': '1.0.0',
        'endpoints': {
            'GET /api/stocks': 'List all stocks',
            'GET /api/recommend/<code>': 'Get recommendation for a stock',
            'GET /api/market/summary': 'Get market summary',
            'GET /api/market/top-buys': 'Get top buy recommendations',
            'GET /api/market/top-sells': 'Get top sell recommendations',
            'GET /api/portfolio': 'Get portfolio summary',
            'GET /api/portfolio/positions': 'Get all positions',
            'POST /api/portfolio/buy': 'Execute buy order',
            'POST /api/portfolio/sell': 'Execute sell order',
        }
    })


if __name__ == '__main__':
    print("=" * 60)
    print("  Intelligent Trading Assistant API")
    print("  IHEC CODELAB 2.0")
    print("=" * 60)
    print("\n  Starting server on http://localhost:5000")
    print("  Press Ctrl+C to stop\n")

    app.run(debug=True, host='0.0.0.0', port=5000)
