"""
Portfolio Simulator
====================
Tracks virtual portfolio performance for the hackathon demo.
Supports buy/sell operations, performance metrics, and allocation tracking.
"""

from datetime import datetime
from typing import Dict, List, Optional
import json


class Portfolio:
    """
    Virtual portfolio for simulating trading operations.

    Attributes:
        initial_capital: Starting capital in TND
        cash: Current cash balance
        holdings: Dict of {stock_code: {'quantity': int, 'avg_price': float, 'stock_name': str}}
        transaction_history: List of all transactions
    """

    def __init__(self, initial_capital: float = 10000.0, name: str = "Mon Portefeuille"):
        """
        Initialize portfolio with TND capital.

        Args:
            initial_capital: Starting capital in TND (default 10,000)
            name: Portfolio name for display
        """
        self.name = name
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.holdings: Dict[str, Dict] = {}
        self.transaction_history: List[Dict] = []
        self.daily_snapshots: List[Dict] = []  # For performance tracking
        self.daily_values: List[Dict] = []  # [{'date': str, 'value': float}]
        self.created_at = datetime.now().isoformat()

    def buy(
        self,
        stock_code: str,
        stock_name: str,
        price: float,
        quantity: int,
        date: str = None
    ) -> Dict:
        """
        Execute a buy order.

        Args:
            stock_code: ISIN code
            stock_name: Human-readable stock name
            price: Price per share in TND
            quantity: Number of shares to buy
            date: Transaction date (defaults to now)

        Returns:
            {'success': bool, 'message': str, 'transaction': dict}
        """
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')

        total_cost = price * quantity

        # Check if we have enough cash
        if total_cost > self.cash:
            return {
                'success': False,
                'message': f'Fonds insuffisants. Requis: {total_cost:.2f} TND, Disponible: {self.cash:.2f} TND',
                'required': total_cost,
                'available': self.cash
            }

        # Deduct cash
        self.cash -= total_cost

        # Update or create holding
        if stock_code not in self.holdings:
            self.holdings[stock_code] = {
                'stock_name': stock_name,
                'quantity': 0,
                'avg_price': 0.0,
                'first_buy_date': date
            }

        holding = self.holdings[stock_code]

        # Calculate new average price
        total_quantity = holding['quantity'] + quantity
        total_value = (holding['quantity'] * holding['avg_price']) + (quantity * price)
        holding['avg_price'] = total_value / total_quantity if total_quantity > 0 else 0
        holding['quantity'] = total_quantity
        holding['last_buy_date'] = date

        # Record transaction
        transaction = {
            'type': 'BUY',
            'stock_code': stock_code,
            'stock_name': stock_name,
            'quantity': quantity,
            'price': price,
            'total': total_cost,
            'date': date,
            'timestamp': datetime.now().isoformat(),
            'cash_after': self.cash
        }
        self.transaction_history.append(transaction)
        self._record_daily_value(date, {stock_code: price})

        return {
            'success': True,
            'message': f'Achat reussi: {quantity} actions de {stock_name} a {price:.2f} TND',
            'transaction': transaction
        }

    def sell(
        self,
        stock_code: str,
        price: float,
        quantity: int,
        date: str = None
    ) -> Dict:
        """
        Execute a sell order.

        Args:
            stock_code: ISIN code
            price: Price per share in TND
            quantity: Number of shares to sell
            date: Transaction date (defaults to now)

        Returns:
            {'success': bool, 'message': str, 'transaction': dict, 'profit_loss': float}
        """
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')

        # Check if we own this stock
        if stock_code not in self.holdings:
            return {
                'success': False,
                'message': f'Vous ne possedez pas d\'actions de ce titre',
                'stock_code': stock_code
            }

        holding = self.holdings[stock_code]

        # Check if we have enough shares
        if holding['quantity'] < quantity:
            return {
                'success': False,
                'message': f'Quantite insuffisante. Disponible: {holding["quantity"]}, Demande: {quantity}',
                'available': holding['quantity']
            }

        # Calculate profit/loss for this transaction
        avg_cost = holding['avg_price'] * quantity
        proceeds = price * quantity
        profit_loss = proceeds - avg_cost

        # Add cash
        self.cash += proceeds

        # Update holding
        stock_name = holding['stock_name']
        holding['quantity'] -= quantity

        # Remove from holdings if quantity reaches 0
        if holding['quantity'] == 0:
            del self.holdings[stock_code]

        # Record transaction
        transaction = {
            'type': 'SELL',
            'stock_code': stock_code,
            'stock_name': stock_name,
            'quantity': quantity,
            'price': price,
            'total': proceeds,
            'profit_loss': profit_loss,
            'date': date,
            'timestamp': datetime.now().isoformat(),
            'cash_after': self.cash
        }
        self.transaction_history.append(transaction)
        self._record_daily_value(date, {stock_code: price})

        return {
            'success': True,
            'message': f'Vente reussie: {quantity} actions a {price:.2f} TND (P/L: {profit_loss:+.2f} TND)',
            'transaction': transaction,
            'profit_loss': profit_loss
        }

    def get_current_value(self, current_prices: Dict[str, float]) -> float:
        """
        Calculate total portfolio value.

        Args:
            current_prices: Dict of {stock_code: current_price}

        Returns:
            Total portfolio value in TND
        """
        holdings_value = sum(
            holding['quantity'] * current_prices.get(stock_code, holding['avg_price'])
            for stock_code, holding in self.holdings.items()
        )
        return self.cash + holdings_value

    def get_holdings_value(self, current_prices: Dict[str, float]) -> float:
        """Get value of holdings only (excluding cash)"""
        return sum(
            holding['quantity'] * current_prices.get(stock_code, holding['avg_price'])
            for stock_code, holding in self.holdings.items()
        )

    def get_performance_metrics(self, current_prices: Dict[str, float]) -> Dict:
        """
        Calculate key performance metrics.

        Args:
            current_prices: Dict of {stock_code: current_price}

        Returns:
            {
                'total_value': float,
                'total_gain_loss': float,
                'roi_percentage': float,
                'win_rate': float,
                ... more metrics
            }
        """
        current_value = self.get_current_value(current_prices)
        holdings_value = self.get_holdings_value(current_prices)
        total_gain_loss = current_value - self.initial_capital
        roi_percentage = (total_gain_loss / self.initial_capital) * 100

        # Calculate win rate from closed positions
        profitable_trades = 0
        total_closed_trades = 0
        total_realized_profit = 0

        for tx in self.transaction_history:
            if tx['type'] == 'SELL':
                total_closed_trades += 1
                pl = tx.get('profit_loss', 0)
                total_realized_profit += pl
                if pl > 0:
                    profitable_trades += 1

        win_rate = (profitable_trades / total_closed_trades * 100) if total_closed_trades > 0 else 0

        # Unrealized P/L
        unrealized_pl = 0
        for stock_code, holding in self.holdings.items():
            current_price = current_prices.get(stock_code, holding['avg_price'])
            cost_basis = holding['quantity'] * holding['avg_price']
            market_value = holding['quantity'] * current_price
            unrealized_pl += market_value - cost_basis

        return {
            'portfolio_name': self.name,
            'initial_capital': self.initial_capital,
            'total_value': round(current_value, 2),
            'cash': round(self.cash, 2),
            'holdings_value': round(holdings_value, 2),
            'total_gain_loss': round(total_gain_loss, 2),
            'roi_percentage': round(roi_percentage, 2),
            'realized_profit': round(total_realized_profit, 2),
            'unrealized_profit': round(unrealized_pl, 2),
            'win_rate': round(win_rate, 1),
            'sharpe_ratio': round(self._calculate_sharpe_ratio(), 4),
            'max_drawdown': round(self._calculate_max_drawdown(), 2),
            'num_positions': len(self.holdings),
            'num_transactions': len(self.transaction_history),
            'num_closed_trades': total_closed_trades,
        }

    def get_allocation(self, current_prices: Dict[str, float]) -> Dict:
        """
        Get portfolio allocation percentages.

        Args:
            current_prices: Dict of {stock_code: current_price}

        Returns:
            {stock_code: percentage, 'CASH': percentage}
        """
        total_value = self.get_current_value(current_prices)

        if total_value <= 0:
            return {'CASH': 100.0}

        allocation = {
            'CASH': round((self.cash / total_value * 100), 2)
        }

        for stock_code, holding in self.holdings.items():
            current_price = current_prices.get(stock_code, holding['avg_price'])
            value = holding['quantity'] * current_price
            allocation[stock_code] = round((value / total_value * 100), 2)

        return allocation

    def get_position_details(self, current_prices: Dict[str, float]) -> List[Dict]:
        """
        Get detailed info for each position.

        Args:
            current_prices: Dict of {stock_code: current_price}

        Returns:
            List of position details
        """
        positions = []

        for stock_code, holding in self.holdings.items():
            current_price = current_prices.get(stock_code, holding['avg_price'])
            current_value = holding['quantity'] * current_price
            cost_basis = holding['quantity'] * holding['avg_price']
            gain_loss = current_value - cost_basis
            gain_loss_pct = (gain_loss / cost_basis * 100) if cost_basis > 0 else 0

            positions.append({
                'stock_code': stock_code,
                'stock_name': holding['stock_name'],
                'quantity': holding['quantity'],
                'avg_price': round(holding['avg_price'], 3),
                'current_price': round(current_price, 3),
                'cost_basis': round(cost_basis, 2),
                'current_value': round(current_value, 2),
                'gain_loss': round(gain_loss, 2),
                'gain_loss_pct': round(gain_loss_pct, 2),
                'is_profitable': gain_loss > 0
            })

        # Sort by value (largest first)
        positions.sort(key=lambda x: x['current_value'], reverse=True)

        return positions

    def get_transaction_history(self, limit: int = None, stock_code: str = None) -> List[Dict]:
        """
        Get transaction history with optional filtering.

        Args:
            limit: Max number of transactions to return
            stock_code: Filter by stock code

        Returns:
            List of transactions (most recent first)
        """
        history = self.transaction_history.copy()

        if stock_code:
            history = [t for t in history if t['stock_code'] == stock_code]

        # Sort by date (most recent first)
        history.sort(key=lambda x: x['timestamp'], reverse=True)

        if limit:
            history = history[:limit]

        return history

    def take_snapshot(self, current_prices: Dict[str, float], date: str = None):
        """
        Take a snapshot of portfolio for historical tracking.

        Args:
            current_prices: Current market prices
            date: Snapshot date (defaults to now)
        """
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')

        snapshot = {
            'date': date,
            'total_value': self.get_current_value(current_prices),
            'cash': self.cash,
            'holdings_value': self.get_holdings_value(current_prices),
            'num_positions': len(self.holdings),
            'timestamp': datetime.now().isoformat()
        }

        self.daily_snapshots.append(snapshot)

    def get_value_history(self) -> List[Dict]:
        """Get historical portfolio values for charting"""
        return self.daily_snapshots

    def to_dict(self) -> Dict:
        """Serialize portfolio to dictionary for storage"""
        return {
            'name': self.name,
            'initial_capital': self.initial_capital,
            'cash': self.cash,
            'holdings': self.holdings,
            'transaction_history': self.transaction_history,
            'daily_snapshots': self.daily_snapshots,
            'daily_values': self.daily_values,
            'created_at': self.created_at
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Portfolio':
        """Deserialize portfolio from dictionary"""
        portfolio = cls(
            initial_capital=data.get('initial_capital', 10000),
            name=data.get('name', 'Mon Portefeuille')
        )
        portfolio.cash = data.get('cash', portfolio.initial_capital)
        portfolio.holdings = data.get('holdings', {})
        portfolio.transaction_history = data.get('transaction_history', [])
        portfolio.daily_snapshots = data.get('daily_snapshots', [])
        portfolio.daily_values = data.get('daily_values', [])
        if not portfolio.daily_values and portfolio.daily_snapshots:
            portfolio.daily_values = [
                {'date': snap.get('date', ''), 'value': float(snap.get('total_value', 0.0))}
                for snap in portfolio.daily_snapshots
            ]
        portfolio.created_at = data.get('created_at', datetime.now().isoformat())
        return portfolio

    def _record_daily_value(self, date: str, price_overrides: Optional[Dict[str, float]] = None):
        """
        Record or update a daily portfolio value entry.

        Args:
            date: Date string in YYYY-MM-DD format
            price_overrides: Optional dict of {stock_code: price} to override for valuation
        """
        prices = {code: holding['avg_price'] for code, holding in self.holdings.items()}
        if price_overrides:
            prices.update(price_overrides)

        value = self.get_current_value(prices)
        for entry in reversed(self.daily_values):
            if entry.get('date') == date:
                entry['value'] = value
                return
        self.daily_values.append({'date': date, 'value': value})

    def _calculate_sharpe_ratio(self) -> float:
        """
        Calculate annualized Sharpe Ratio from daily values.
        Assumes risk-free rate = 0.
        """
        if len(self.daily_values) < 2:
            return 0.0

        values = [float(v.get('value', 0.0)) for v in sorted(self.daily_values, key=lambda x: x.get('date', ''))]
        returns = []
        for i in range(1, len(values)):
            prev = values[i - 1]
            if prev == 0:
                continue
            returns.append((values[i] - prev) / prev)

        if len(returns) < 2:
            return 0.0

        mean_return = sum(returns) / len(returns)
        variance = sum((r - mean_return) ** 2 for r in returns) / len(returns)
        std_dev = variance ** 0.5
        if std_dev == 0:
            return 0.0

        return (mean_return / std_dev) * (252 ** 0.5)

    def _calculate_max_drawdown(self) -> float:
        """
        Calculate maximum drawdown percentage from daily values.
        """
        if len(self.daily_values) < 2:
            return 0.0

        values = [float(v.get('value', 0.0)) for v in sorted(self.daily_values, key=lambda x: x.get('date', ''))]
        peak = values[0] if values else 0.0
        max_drawdown = 0.0

        for value in values:
            if value > peak:
                peak = value
            if peak > 0:
                drawdown = (peak - value) / peak
                if drawdown > max_drawdown:
                    max_drawdown = drawdown

        return max_drawdown * 100

    def save_to_file(self, filepath: str):
        """Save portfolio to JSON file"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)

    @classmethod
    def load_from_file(cls, filepath: str) -> 'Portfolio':
        """Load portfolio from JSON file"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls.from_dict(data)

    def get_summary_string(self, current_prices: Dict[str, float]) -> str:
        """Get a human-readable summary for display"""
        metrics = self.get_performance_metrics(current_prices)

        lines = [
            f"=== {self.name} ===",
            f"Valeur totale: {metrics['total_value']:,.2f} TND",
            f"Cash: {metrics['cash']:,.2f} TND",
            f"Positions: {metrics['holdings_value']:,.2f} TND",
            "",
            f"Performance:",
            f"  ROI: {metrics['roi_percentage']:+.2f}%",
            f"  Gain/Perte: {metrics['total_gain_loss']:+,.2f} TND",
            f"  Taux de reussite: {metrics['win_rate']:.1f}%",
            "",
            f"Activite:",
            f"  Positions ouvertes: {metrics['num_positions']}",
            f"  Transactions: {metrics['num_transactions']}",
        ]

        return '\n'.join(lines)


# ============================================================================
# PORTFOLIO MANAGER (for multiple portfolios)
# ============================================================================

class PortfolioManager:
    """
    Manages multiple portfolios for comparison and backtesting.
    """

    def __init__(self):
        self.portfolios: Dict[str, Portfolio] = {}

    def create_portfolio(self, name: str, initial_capital: float = 10000) -> Portfolio:
        """Create a new portfolio"""
        portfolio = Portfolio(initial_capital=initial_capital, name=name)
        self.portfolios[name] = portfolio
        return portfolio

    def get_portfolio(self, name: str) -> Optional[Portfolio]:
        """Get a portfolio by name"""
        return self.portfolios.get(name)

    def list_portfolios(self) -> List[str]:
        """List all portfolio names"""
        return list(self.portfolios.keys())

    def compare_portfolios(self, current_prices: Dict[str, float]) -> List[Dict]:
        """Compare all portfolios performance"""
        comparisons = []
        for name, portfolio in self.portfolios.items():
            metrics = portfolio.get_performance_metrics(current_prices)
            comparisons.append({
                'name': name,
                **metrics
            })

        # Sort by ROI
        comparisons.sort(key=lambda x: x['roi_percentage'], reverse=True)
        return comparisons
