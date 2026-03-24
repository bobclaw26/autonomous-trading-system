"""Backtesting engine for strategy validation on historical data."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Callable
import statistics

from src.engine.execution import ExecutionEngine, SlippageModel
from src.engine.order import OrderSide, OrderType


@dataclass
class BacktestConfig:
    """Configuration for backtesting."""
    initial_capital: float = 100_000.0
    start_date: datetime = None
    end_date: datetime = None
    symbols: List[str] = field(default_factory=list)
    slippage_model: Optional[SlippageModel] = None
    commission_pct: float = 0.001  # 0.1%
    
    def __post_init__(self):
        if self.slippage_model is None:
            self.slippage_model = SlippageModel()


@dataclass
class BacktestResult:
    """Results from a backtest run."""
    start_date: datetime
    end_date: datetime
    initial_capital: float
    final_capital: float
    total_return_pct: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    profit_factor: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    avg_win: float
    avg_loss: float
    daily_returns: List[float] = field(default_factory=list)
    equity_curve: List[float] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat(),
            "initial_capital": self.initial_capital,
            "final_capital": self.final_capital,
            "total_return_pct": self.total_return_pct,
            "sharpe_ratio": self.sharpe_ratio,
            "max_drawdown": self.max_drawdown,
            "win_rate": self.win_rate,
            "profit_factor": self.profit_factor,
            "total_trades": self.total_trades,
            "winning_trades": self.winning_trades,
            "losing_trades": self.losing_trades,
            "avg_win": self.avg_win,
            "avg_loss": self.avg_loss,
        }


class BacktestEngine:
    """Engine for running backtests on historical data."""
    
    def __init__(self, config: BacktestConfig):
        self.config = config
        self.engine = ExecutionEngine(
            initial_capital=config.initial_capital,
            slippage_model=config.slippage_model
        )
        self.daily_returns: List[float] = []
        self.equity_curve: List[float] = []
        self.trades_executed: int = 0
    
    def run_backtest(
        self,
        price_data: Dict[str, List[Dict]],
        strategy_fn: Callable
    ) -> BacktestResult:
        """
        Run backtest with given price data and strategy.
        
        Args:
            price_data: Dict of symbol -> list of OHLCV candles
            strategy_fn: Function that takes (engine, prices, date) and executes trades
        
        Returns:
            BacktestResult with performance metrics
        """
        # Get date range from price data
        all_dates = set()
        for symbol, candles in price_data.items():
            for candle in candles:
                all_dates.add(candle["date"])
        
        sorted_dates = sorted(all_dates)
        if not sorted_dates:
            raise ValueError("No price data provided")
        
        start_date = sorted_dates[0]
        end_date = sorted_dates[-1]
        
        prev_portfolio_value = self.config.initial_capital
        
        # Replay trades for each date
        for date in sorted_dates:
            # Get prices for this date
            current_prices = {}
            for symbol, candles in price_data.items():
                for candle in candles:
                    if candle["date"] == date:
                        current_prices[symbol] = candle["close"]
                        break
            
            if not current_prices:
                continue
            
            # Execute strategy for this date
            strategy_fn(self.engine, current_prices, date)
            
            # Calculate daily return
            portfolio_value = self.engine.get_portfolio_value(current_prices)
            if prev_portfolio_value > 0:
                daily_return = (portfolio_value - prev_portfolio_value) / prev_portfolio_value
                self.daily_returns.append(daily_return)
            
            self.equity_curve.append(portfolio_value)
            prev_portfolio_value = portfolio_value
        
        # Calculate final metrics
        final_capital = self.engine.get_portfolio_value(current_prices)
        total_return_pct = ((final_capital - self.config.initial_capital) / 
                           self.config.initial_capital) * 100
        
        sharpe_ratio = self._calculate_sharpe_ratio()
        max_drawdown = self._calculate_max_drawdown()
        win_rate, profit_factor = self._calculate_trade_stats()
        
        # Get trade statistics
        closed_positions = self.engine.positions.get_closed_positions()
        winning_trades = sum(1 for p in closed_positions if p.get_realized_pnl() > 0)
        losing_trades = sum(1 for p in closed_positions if p.get_realized_pnl() < 0)
        
        # Calculate average win/loss
        winning_pnls = [p.get_realized_pnl() for p in closed_positions if p.get_realized_pnl() > 0]
        losing_pnls = [p.get_realized_pnl() for p in closed_positions if p.get_realized_pnl() < 0]
        
        avg_win = statistics.mean(winning_pnls) if winning_pnls else 0
        avg_loss = statistics.mean(losing_pnls) if losing_pnls else 0
        
        return BacktestResult(
            start_date=start_date,
            end_date=end_date,
            initial_capital=self.config.initial_capital,
            final_capital=final_capital,
            total_return_pct=total_return_pct,
            sharpe_ratio=sharpe_ratio,
            max_drawdown=max_drawdown,
            win_rate=win_rate,
            profit_factor=profit_factor,
            total_trades=len(self.engine.order_history),
            winning_trades=winning_trades,
            losing_trades=losing_trades,
            avg_win=avg_win,
            avg_loss=avg_loss,
            daily_returns=self.daily_returns,
            equity_curve=self.equity_curve,
        )
    
    def _calculate_sharpe_ratio(self, risk_free_rate: float = 0.02) -> float:
        """Calculate Sharpe ratio."""
        if not self.daily_returns or len(self.daily_returns) < 2:
            return 0.0
        
        mean_return = statistics.mean(self.daily_returns)
        std_dev = statistics.stdev(self.daily_returns)
        
        if std_dev == 0:
            return 0.0
        
        annual_return = mean_return * 252
        annual_volatility = std_dev * (252 ** 0.5)
        
        return (annual_return - risk_free_rate) / annual_volatility if annual_volatility > 0 else 0.0
    
    def _calculate_max_drawdown(self) -> float:
        """Calculate maximum drawdown."""
        if not self.equity_curve:
            return 0.0
        
        peak = self.equity_curve[0]
        max_dd = 0.0
        
        for value in self.equity_curve:
            if value > peak:
                peak = value
            
            drawdown = (peak - value) / peak if peak > 0 else 0
            max_dd = max(max_dd, drawdown)
        
        return max_dd * 100
    
    def _calculate_trade_stats(self) -> tuple:
        """Calculate win rate and profit factor."""
        closed_positions = self.engine.positions.get_closed_positions()
        
        if not closed_positions:
            return 0.0, 0.0
        
        pnls = [p.get_realized_pnl() for p in closed_positions]
        winning = sum(1 for pnl in pnls if pnl > 0)
        win_rate = (winning / len(pnls)) * 100 if pnls else 0
        
        gross_profit = sum(pnl for pnl in pnls if pnl > 0)
        gross_loss = abs(sum(pnl for pnl in pnls if pnl < 0))
        
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else (1.0 if gross_profit > 0 else 0.0)
        
        return win_rate, profit_factor
    
    def reset(self):
        """Reset backtest engine for new run."""
        self.engine = ExecutionEngine(
            initial_capital=self.config.initial_capital,
            slippage_model=self.config.slippage_model
        )
        self.daily_returns = []
        self.equity_curve = []
        self.trades_executed = 0


class WalkForwardBacktester:
    """Performs walk-forward analysis for strategy validation."""
    
    def __init__(self, config: BacktestConfig):
        self.config = config
        self.results: List[BacktestResult] = []
    
    def run_walk_forward(
        self,
        price_data: Dict[str, List[Dict]],
        strategy_fn: Callable,
        window_size: int = 252,  # 1 year
        step_size: int = 63       # 1 quarter
    ) -> Dict:
        """
        Run walk-forward analysis.
        
        Args:
            price_data: Historical price data
            strategy_fn: Strategy function
            window_size: Training window size in trading days
            step_size: Step forward size in trading days
        
        Returns:
            Dictionary with walk-forward results
        """
        # Get all unique dates
        all_dates = set()
        for symbol, candles in price_data.items():
            for candle in candles:
                all_dates.add(candle["date"])
        
        sorted_dates = sorted(all_dates)
        
        # Perform walk-forward
        for i in range(0, len(sorted_dates) - window_size, step_size):
            train_dates = sorted_dates[i:i+window_size]
            test_dates = sorted_dates[i+window_size:i+window_size+step_size]
            
            if not test_dates:
                break
            
            # Filter data for this window
            train_data = self._filter_by_dates(price_data, train_dates)
            test_data = self._filter_by_dates(price_data, test_dates)
            
            # Train (for future ML strategies)
            # For now, just run test
            
            # Test
            backtest = BacktestEngine(self.config)
            result = backtest.run_backtest(test_data, strategy_fn)
            self.results.append(result)
        
        # Calculate aggregate statistics
        return self._aggregate_results()
    
    def _filter_by_dates(self, price_data: Dict, dates: List) -> Dict:
        """Filter price data to specific dates."""
        filtered = {}
        date_set = set(dates)
        
        for symbol, candles in price_data.items():
            filtered[symbol] = [c for c in candles if c["date"] in date_set]
        
        return filtered
    
    def _aggregate_results(self) -> Dict:
        """Aggregate walk-forward results."""
        if not self.results:
            return {}
        
        total_return = sum(r.total_return_pct for r in self.results) / len(self.results)
        avg_sharpe = sum(r.sharpe_ratio for r in self.results) / len(self.results)
        avg_drawdown = sum(r.max_drawdown for r in self.results) / len(self.results)
        
        return {
            "num_windows": len(self.results),
            "avg_return_pct": total_return,
            "avg_sharpe_ratio": avg_sharpe,
            "avg_max_drawdown": avg_drawdown,
            "results": [r.to_dict() for r in self.results],
        }
