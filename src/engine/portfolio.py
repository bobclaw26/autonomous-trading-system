"""Portfolio management and analytics."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional
import statistics
from .execution import ExecutionEngine


@dataclass
class PortfolioSnapshot:
    """A snapshot of portfolio state at a point in time."""
    timestamp: datetime
    portfolio_value: float
    cash: float
    total_pnl: float
    realized_pnl: float
    unrealized_pnl: float
    return_percent: float
    open_positions_count: int
    closed_positions_count: int


class PortfolioManager:
    """Manages portfolio analytics and performance tracking."""
    
    def __init__(self, engine: ExecutionEngine):
        self.engine = engine
        self.snapshots: List[PortfolioSnapshot] = []
        self.daily_returns: List[float] = []
    
    def take_snapshot(self, prices: Dict[str, float]) -> PortfolioSnapshot:
        """Take a snapshot of current portfolio state."""
        portfolio_value = self.engine.get_portfolio_value(prices)
        total_pnl = self.engine.get_total_pnl(prices)
        realized_pnl = self.engine.positions.get_total_realized_pnl()
        unrealized_pnl = self.engine.positions.get_total_unrealized_pnl(prices)
        return_percent = self.engine.get_return_percent(prices)
        
        snapshot = PortfolioSnapshot(
            timestamp=datetime.utcnow(),
            portfolio_value=portfolio_value,
            cash=self.engine.cash,
            total_pnl=total_pnl,
            realized_pnl=realized_pnl,
            unrealized_pnl=unrealized_pnl,
            return_percent=return_percent,
            open_positions_count=len(self.engine.positions.get_open_positions()),
            closed_positions_count=len(self.engine.positions.get_closed_positions())
        )
        
        self.snapshots.append(snapshot)
        return snapshot
    
    def record_daily_return(self, daily_return: float):
        """Record a daily return."""
        self.daily_returns.append(daily_return)
    
    def get_sharpe_ratio(self, risk_free_rate: float = 0.02) -> float:
        """
        Calculate Sharpe ratio.
        
        Args:
            risk_free_rate: Annual risk-free rate (default 2%)
        
        Returns:
            Sharpe ratio
        """
        if not self.daily_returns or len(self.daily_returns) < 2:
            return 0.0
        
        mean_return = statistics.mean(self.daily_returns)
        std_dev = statistics.stdev(self.daily_returns)
        
        if std_dev == 0:
            return 0.0
        
        # Annualized Sharpe ratio (252 trading days per year)
        annual_excess_return = (mean_return * 252) - risk_free_rate
        annual_volatility = std_dev * (252 ** 0.5)
        
        return annual_excess_return / annual_volatility if annual_volatility > 0 else 0.0
    
    def get_max_drawdown(self) -> float:
        """
        Calculate maximum drawdown.
        
        Returns:
            Maximum drawdown as a percentage
        """
        if not self.snapshots:
            return 0.0
        
        peak = self.snapshots[0].portfolio_value
        max_dd = 0.0
        
        for snapshot in self.snapshots:
            if snapshot.portfolio_value > peak:
                peak = snapshot.portfolio_value
            
            drawdown = (peak - snapshot.portfolio_value) / peak
            max_dd = max(max_dd, drawdown)
        
        return max_dd * 100
    
    def get_win_rate(self) -> float:
        """
        Calculate win rate (% of closed trades with profit).
        
        Returns:
            Win rate as a percentage
        """
        closed_positions = self.engine.positions.get_closed_positions()
        if not closed_positions:
            return 0.0
        
        winners = sum(1 for p in closed_positions if p.get_realized_pnl() > 0)
        return (winners / len(closed_positions)) * 100
    
    def get_sortino_ratio(self, target_return: float = 0.0) -> float:
        """
        Calculate Sortino ratio (downside risk only).
        
        Args:
            target_return: Minimum acceptable return
        
        Returns:
            Sortino ratio
        """
        if not self.daily_returns or len(self.daily_returns) < 2:
            return 0.0
        
        mean_return = statistics.mean(self.daily_returns)
        
        # Calculate downside deviation
        downside_returns = [r - target_return for r in self.daily_returns if r < target_return]
        if not downside_returns:
            downside_dev = 0.0
        else:
            downside_dev = (sum(r ** 2 for r in downside_returns) / len(downside_returns)) ** 0.5
        
        if downside_dev == 0:
            return 0.0
        
        # Annualized Sortino ratio
        annual_excess = (mean_return * 252) - target_return
        annual_downside_dev = downside_dev * (252 ** 0.5)
        
        return annual_excess / annual_downside_dev
    
    def get_cagr(self, years: float = 1.0) -> float:
        """
        Calculate Compound Annual Growth Rate.
        
        Args:
            years: Time period in years
        
        Returns:
            CAGR as a percentage
        """
        if not self.snapshots or years == 0:
            return 0.0
        
        start_value = self.engine.initial_capital
        end_value = self.snapshots[-1].portfolio_value
        
        if start_value == 0:
            return 0.0
        
        return (((end_value / start_value) ** (1 / years)) - 1) * 100
    
    def get_profit_factor(self) -> float:
        """
        Calculate profit factor (gross profit / gross loss).
        
        Returns:
            Profit factor (>1 is profitable)
        """
        closed_positions = self.engine.positions.get_closed_positions()
        if not closed_positions:
            return 0.0
        
        gross_profit = sum(p.get_realized_pnl() for p in closed_positions if p.get_realized_pnl() > 0)
        gross_loss = abs(sum(p.get_realized_pnl() for p in closed_positions if p.get_realized_pnl() < 0))
        
        if gross_loss == 0:
            return float('inf') if gross_profit > 0 else 0.0
        
        return gross_profit / gross_loss
    
    def get_avg_trade_size(self) -> float:
        """Get average trade size in dollars."""
        if not self.engine.order_history:
            return 0.0
        
        total_trade_value = sum(
            order.filled_quantity * order.fill_price 
            for order in self.engine.order_history
            if order.is_filled()
        )
        
        return total_trade_value / len(self.engine.order_history)
    
    def get_summary_stats(self, prices: Dict[str, float]) -> Dict:
        """Get comprehensive portfolio summary statistics."""
        return {
            "portfolio_value": self.engine.get_portfolio_value(prices),
            "cash": self.engine.cash,
            "total_pnl": self.engine.get_total_pnl(prices),
            "return_percent": self.engine.get_return_percent(prices),
            "sharpe_ratio": self.get_sharpe_ratio(),
            "sortino_ratio": self.get_sortino_ratio(),
            "max_drawdown": self.get_max_drawdown(),
            "cagr": self.get_cagr(),
            "win_rate": self.get_win_rate(),
            "profit_factor": self.get_profit_factor(),
            "avg_trade_size": self.get_avg_trade_size(),
            "total_trades": len(self.engine.order_history),
            "open_positions": len(self.engine.positions.get_open_positions()),
            "closed_positions": len(self.engine.positions.get_closed_positions()),
        }
