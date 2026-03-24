"""Tests for backtesting engine."""

import pytest
from datetime import datetime, timedelta

from src.backtesting.backtest_engine import BacktestEngine, BacktestConfig
from src.engine.order import OrderSide, OrderType


class TestBacktestEngine:
    """Test BacktestEngine."""
    
    def create_sample_price_data(self, symbol="AAPL", days=100):
        """Create sample OHLCV data."""
        data = {}
        data[symbol] = []
        
        price = 100.0
        start_date = datetime(2023, 1, 1)
        
        for i in range(days):
            date = start_date + timedelta(days=i)
            price += (i % 3 - 1) * 0.5  # Oscillate price
            
            data[symbol].append({
                "date": date,
                "open": price,
                "high": price * 1.02,
                "low": price * 0.98,
                "close": price,
                "volume": 1000000
            })
        
        return data
    
    def test_create_backtest_engine(self):
        """Test creating backtest engine."""
        config = BacktestConfig(initial_capital=100_000)
        engine = BacktestEngine(config)
        
        assert engine.config.initial_capital == 100_000
        assert engine.config.commission_pct == 0.001
    
    def test_simple_backtest(self):
        """Test running a simple backtest."""
        config = BacktestConfig(initial_capital=100_000)
        engine = BacktestEngine(config)
        
        price_data = self.create_sample_price_data()
        
        def buy_and_hold_strategy(exec_engine, prices, date):
            # Buy on first day
            if len(exec_engine.order_history) == 0:
                order = exec_engine.place_order(
                    symbol="AAPL",
                    side=OrderSide.BUY,
                    quantity=100,
                    order_type=OrderType.MARKET,
                    price=prices.get("AAPL", 100)
                )
                exec_engine.execute_market_order(order, current_price=prices.get("AAPL", 100))
        
        result = engine.run_backtest(price_data, buy_and_hold_strategy)
        
        assert result.initial_capital == 100_000
        assert result.total_trades > 0
        assert len(result.equity_curve) > 0
        assert len(result.daily_returns) > 0
    
    def test_backtest_with_multiple_trades(self):
        """Test backtest with entry and exit."""
        config = BacktestConfig(initial_capital=100_000)
        engine = BacktestEngine(config)
        
        price_data = self.create_sample_price_data()
        
        trade_count = [0]  # Mutable counter
        
        def simple_strategy(exec_engine, prices, date):
            # Buy every 10 days, sell after 5 days
            if trade_count[0] % 15 < 5:
                # Check if we can buy
                if len(exec_engine.positions.get_open_positions()) == 0:
                    order = exec_engine.place_order(
                        symbol="AAPL",
                        side=OrderSide.BUY,
                        quantity=50,
                        order_type=OrderType.MARKET,
                        price=prices.get("AAPL", 100)
                    )
                    exec_engine.execute_market_order(order, current_price=prices.get("AAPL", 100))
            elif trade_count[0] % 15 >= 5 and len(exec_engine.positions.get_open_positions()) > 0:
                # Sell
                order = exec_engine.place_order(
                    symbol="AAPL",
                    side=OrderSide.SELL,
                    quantity=50,
                    order_type=OrderType.MARKET,
                    price=prices.get("AAPL", 100)
                )
                exec_engine.execute_market_order(order, current_price=prices.get("AAPL", 100))
            
            trade_count[0] += 1
        
        result = engine.run_backtest(price_data, simple_strategy)
        
        assert result.total_trades >= 1
        assert result.win_rate >= 0
        assert result.profit_factor > 0 or result.profit_factor == 0
    
    def test_sharpe_ratio_calculation(self):
        """Test Sharpe ratio calculation."""
        config = BacktestConfig(initial_capital=100_000)
        engine = BacktestEngine(config)
        
        # Add sample returns
        engine.daily_returns = [0.01, -0.005, 0.015, 0.002, -0.01]
        
        sharpe = engine._calculate_sharpe_ratio()
        assert isinstance(sharpe, (int, float))
    
    def test_max_drawdown_calculation(self):
        """Test max drawdown calculation."""
        config = BacktestConfig(initial_capital=100_000)
        engine = BacktestEngine(config)
        
        # Simulate equity curve: up, up, down, down, up
        engine.equity_curve = [100_000, 110_000, 120_000, 100_000, 80_000, 90_000]
        
        max_dd = engine._calculate_max_drawdown()
        
        # Max drawdown from 120_000 to 80_000 = 33.33%
        assert 30 < max_dd < 35
    
    def test_empty_backtest(self):
        """Test backtest with no trades."""
        config = BacktestConfig(initial_capital=100_000)
        engine = BacktestEngine(config)
        
        price_data = self.create_sample_price_data()
        
        def do_nothing_strategy(exec_engine, prices, date):
            pass
        
        result = engine.run_backtest(price_data, do_nothing_strategy)
        
        assert result.total_trades == 0
        assert result.total_return_pct == 0
    
    def test_reset_engine(self):
        """Test resetting engine between runs."""
        config = BacktestConfig(initial_capital=100_000)
        engine = BacktestEngine(config)
        
        price_data = self.create_sample_price_data()
        
        def simple_trade(exec_engine, prices, date):
            if len(exec_engine.order_history) == 0:
                order = exec_engine.place_order(
                    "AAPL", OrderSide.BUY, 10, OrderType.MARKET, prices.get("AAPL", 100)
                )
                exec_engine.execute_market_order(order, current_price=prices.get("AAPL", 100))
        
        # First run
        result1 = engine.run_backtest(price_data, simple_trade)
        trades1 = result1.total_trades
        
        # Reset and run again
        engine.reset()
        result2 = engine.run_backtest(price_data, simple_trade)
        
        assert result2.total_trades == trades1


class TestWalkForwardBacktester:
    """Test WalkForwardBacktester."""
    
    def create_sample_price_data(self, symbol="AAPL", days=300):
        """Create sample OHLCV data."""
        data = {}
        data[symbol] = []
        
        price = 100.0
        start_date = datetime(2023, 1, 1)
        
        for i in range(days):
            date = start_date + timedelta(days=i)
            price += (i % 5 - 2) * 0.3  # Oscillate price
            
            data[symbol].append({
                "date": date,
                "open": price,
                "high": price * 1.02,
                "low": price * 0.98,
                "close": price,
                "volume": 1000000
            })
        
        return data
    
    def test_walk_forward_analysis(self):
        """Test walk-forward analysis."""
        from src.backtesting.backtest_engine import WalkForwardBacktester
        
        config = BacktestConfig(initial_capital=100_000)
        wf = WalkForwardBacktester(config)
        
        price_data = self.create_sample_price_data()
        
        def simple_strategy(exec_engine, prices, date):
            if len(exec_engine.order_history) == 0:
                order = exec_engine.place_order(
                    "AAPL", OrderSide.BUY, 50, OrderType.MARKET, prices.get("AAPL", 100)
                )
                exec_engine.execute_market_order(order, current_price=prices.get("AAPL", 100))
        
        results = wf.run_walk_forward(price_data, simple_strategy, window_size=60, step_size=30)
        
        assert "num_windows" in results
        assert results["num_windows"] > 0
        assert "avg_return_pct" in results


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
