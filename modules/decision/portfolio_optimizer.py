"""
Portfolio Optimizer
===================
Suggest diversified portfolio allocations based on user profile.
"""

from typing import Dict, List, Optional, Tuple

import numpy as np

from modules.decision.engine import get_top_recommendations
from modules.shared.data_loader import get_stock_data, get_current_price, get_stock_name, get_liquid_stocks


ALLOCATION_TEMPLATES = {
    'conservative': {
        'stable_stocks': 0.30,
        'bonds': 0.40,
        'cash': 0.30,
    },
    'moderate': {
        'stable_stocks': 0.40,
        'bonds': 0.30,
        'cash': 0.30,
    },
    'aggressive': {
        'growth_stocks': 0.60,
        'stable_stocks': 0.20,
        'cash': 0.20,
    },
}


def _compute_volatility(stock_code: str, days: int = 30) -> Optional[float]:
    """Compute volatility as std dev of daily returns."""
    try:
        df = get_stock_data(stock_code)
        if df.empty:
            return None
        series = df['close'].tail(days).astype(float)
        if len(series) < 2:
            return None
        returns = series.pct_change().dropna()
        if returns.empty:
            return None
        return float(np.std(returns))
    except Exception:
        return None


def _categorize_by_volatility(codes: List[str]) -> Tuple[List[str], List[str]]:
    """Split stocks into stable (low vol) and growth (high vol) using median volatility."""
    vols = []
    for code in codes:
        vol = _compute_volatility(code)
        if vol is not None:
            vols.append((code, vol))

    if not vols:
        return [], []

    vol_values = [v for _, v in vols]
    median_vol = float(np.median(vol_values))

    stable = [code for code, vol in vols if vol <= median_vol]
    growth = [code for code, vol in vols if vol > median_vol]

    return stable, growth


def _build_stock_suggestions(
    stock_codes: List[str],
    amount: float,
    total_capital: float,
    description: str
) -> Tuple[List[Dict], float]:
    """Create stock allocation suggestions and return list plus unallocated cash."""
    if amount <= 0 or not stock_codes:
        return [], amount

    per_stock_budget = amount / len(stock_codes)
    suggestions = []
    used = 0.0

    for code in stock_codes:
        price = get_current_price(code)
        if price <= 0:
            continue

        quantity = int(per_stock_budget / price)
        if quantity <= 0:
            continue

        allocated = quantity * price
        used += allocated

        suggestions.append({
            'type': 'STOCK',
            'stock_code': code,
            'stock_name': get_stock_name(code),
            'quantity': quantity,
            'amount': round(allocated, 2),
            'percentage': round((allocated / total_capital) * 100, 2),
            'description': description,
        })

    leftover = max(amount - used, 0.0)
    return suggestions, leftover


def suggest_diversified_portfolio(user_profile: str, capital: float = 10000) -> List[Dict]:
    """
    Suggest diversified portfolio allocations based on user profile.

    Args:
        user_profile: 'conservative' | 'moderate' | 'aggressive'
        capital: Total capital to allocate

    Returns:
        List of allocation suggestions.
    """
    profile = user_profile.lower().strip()
    allocation = ALLOCATION_TEMPLATES.get(profile, ALLOCATION_TEMPLATES['moderate'])

    # Get top buy recommendations and filter by liquidity
    try:
        top_recs = get_top_recommendations(n=20, user_profile=profile, recommendation_type='buy')
    except Exception:
        top_recs = []

    liquid = set(get_liquid_stocks(min_avg_volume=1000, min_days=30))
    candidates = [r['stock_code'] for r in top_recs if r.get('stock_code') in liquid]

    stable_candidates, growth_candidates = _categorize_by_volatility(candidates)

    suggestions: List[Dict] = []
    remaining_cash = 0.0

    # Allocate stable stocks
    stable_pct = allocation.get('stable_stocks', 0.0)
    stable_amount = capital * stable_pct
    if stable_pct > 0:
        stable_list = stable_candidates[:5]
        stable_desc = "Actions stables (faible volatilité)"
        stable_suggestions, leftover = _build_stock_suggestions(
            stable_list, stable_amount, capital, stable_desc
        )
        suggestions.extend(stable_suggestions)
        remaining_cash += leftover

    # Allocate growth stocks (aggressive only)
    growth_pct = allocation.get('growth_stocks', 0.0)
    growth_amount = capital * growth_pct
    if growth_pct > 0:
        growth_list = growth_candidates[:5]
        growth_desc = "Actions de croissance (volatilité élevée)"
        growth_suggestions, leftover = _build_stock_suggestions(
            growth_list, growth_amount, capital, growth_desc
        )
        suggestions.extend(growth_suggestions)
        remaining_cash += leftover

    # Bonds allocation (represented as cash)
    bonds_pct = allocation.get('bonds', 0.0)
    bonds_amount = capital * bonds_pct
    if bonds_amount > 0:
        suggestions.append({
            'type': 'BONDS',
            'stock_code': None,
            'stock_name': None,
            'quantity': None,
            'amount': round(bonds_amount, 2),
            'percentage': round((bonds_amount / capital) * 100, 2),
            'description': "Obligations (représentées en cash pour MVP)",
        })

    # Cash allocation (includes unallocated/rounding)
    cash_pct = allocation.get('cash', 0.0)
    cash_amount = capital * cash_pct + remaining_cash
    if cash_amount > 0:
        suggestions.append({
            'type': 'CASH',
            'stock_code': None,
            'stock_name': None,
            'quantity': None,
            'amount': round(cash_amount, 2),
            'percentage': round((cash_amount / capital) * 100, 2),
            'description': "Réserves de liquidités pour opportunités/risques",
        })

    return suggestions
