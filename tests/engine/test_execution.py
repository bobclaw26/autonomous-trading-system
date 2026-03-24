"""Tests for order execution engine."""

import pytest
from src.engine.order import OrderType, OrderSide, OrderStatus
from src.engine.execution import ExecutionEngine, SlippageModel


class TestSlippageModel:
    """Test SlippageModel."""
    
    def test_base_spread(self):
        """Test base spread calculation."""
        model = SlippageModel(base_spread_bps=1.0)
        slippage = model.calculate_slippage(
            quantity=100,
            price=150,
            side=OrderSide.BUY,
            volatility=0
        )
        # Should be at least base spread
        assert slippage >= 1.0
    
    def test_market_impact(self):
        """Test market impact increases with size."""
        model = SlippageModel(base_spread_bps=1.0, market_impact_bps=0.5)
        
        small_slippage = model.calculate_slippage(
            quantity=10,
            price=150,
            side=OrderSide.BUY,
            volatility=0
        )
        
        large_slippage = model.calculate_slippage(
            quantity=1000,
            price=150,
            side=OrderSide.BUY,
            volatility=0
        )
        
        assert large_slippage > small_slippage
    
    def test_volatility_impact(self):
        """Test volatility increases slippage on average."""
        model = SlippageModel(base_spread_bps=1.0, volatility_multiplier=2.0)
        
        # Test multiple times due to randomness and take average
        low_vol_samples = [
            model.calculate_slippage(
                quantity=100,
                price=150,
                side=OrderSide.BUY,
                volatility=10
            ) for _ in range(10)
        ]
        
        high_vol_samples = [
            model.calculate_slippage(
                quantity=100,
                price=150,
                side=OrderSide.BUY,
                volatility=50
            ) for _ in range(10)
        ]
        
        # Average should show volatility impact
        assert sum(high_vol_samples) / len(high_vol_samples) > sum(low_vol_samples) / len(low_vol_samples)


class TestExecutionEngine:
    """Test ExecutionEngine."""
    
    def test_create_engine(self):
        """Test creating an execution engine."""
        engine = ExecutionEngine(initial_capital=100_000)
        assert engine.cash == 100_000
        assert engine.initial_capital == 100_000
    
    def test_place_market_order(self):
        """Test placing a market order."""
        engine = ExecutionEngine(initial_capital=100_000)
        order = engine.place_order(
            symbol="AAPL",
            side=OrderSide.BUY,
            quantity=100,
            order_type=OrderType.MARKET,
            price=150
        )
        
        assert order.symbol == "AAPL"
        assert order.quantity == 100
        assert order.status == OrderStatus.PENDING
    
    def test_execute_buy_order(self):
        """Test executing a buy order."""
        engine = ExecutionEngine(initial_capital=100_000)
        order = engine.place_order(
            symbol="AAPL",
            side=OrderSide.BUY,
            quantity=100,
            order_type=OrderType.MARKET,
            price=150
        )
        
        report = engine.execute_market_order(order, current_price=150, volatility=0)
        
        assert order.is_filled()
        assert report.quantity_filled == 100
        assert engine.cash < 100_000  # Cash reduced after purchase
    
    def test_execute_sell_order(self):
        """Test executing a sell order."""
        engine = ExecutionEngine(initial_capital=100_000)
        
        # First buy
        buy_order = engine.place_order(
            symbol="AAPL",
            side=OrderSide.BUY,
            quantity=100,
            order_type=OrderType.MARKET,
            price=150
        )
        engine.execute_market_order(buy_order, current_price=150)
        cash_after_buy = engine.cash
        
        # Then sell
        sell_order = engine.place_order(
            symbol="AAPL",
            side=OrderSide.SELL,
            quantity=100,
            order_type=OrderType.MARKET,
            price=160
        )
        engine.execute_market_order(sell_order, current_price=160)
        cash_after_sell = engine.cash
        
        assert cash_after_sell > cash_after_buy
    
    def test_insufficient_funds(self):
        """Test order rejection when insufficient funds."""
        engine = ExecutionEngine(initial_capital=10_000)
        order = engine.place_order(
            symbol="AAPL",
            side=OrderSide.BUY,
            quantity=100,
            order_type=OrderType.MARKET,
            price=200  # 100 * 200 = 20,000 > 10,000
        )
        
        report = engine.execute_market_order(order, current_price=200)
        assert order.status == OrderStatus.REJECTED
    
    def test_slippage_on_buy(self):
        """Test that slippage increases execution price on buy."""
        engine = ExecutionEngine(
            initial_capital=100_000,
            slippage_model=SlippageModel(base_spread_bps=10)  # 0.1% spread
        )
        
        order = engine.place_order(
            symbol="AAPL",
            side=OrderSide.BUY,
            quantity=100,
            order_type=OrderType.MARKET,
            price=150
        )
        
        report = engine.execute_market_order(order, current_price=150)
        # Execution price should be higher due to slippage
        assert report.execution_price > 150
    
    def test_slippage_on_sell(self):
        """Test that slippage decreases execution price on sell."""
        engine = ExecutionEngine(
            initial_capital=100_000,
            slippage_model=SlippageModel(base_spread_bps=10)
        )
        
        # First buy
        buy_order = engine.place_order(
            symbol="AAPL",
            side=OrderSide.BUY,
            quantity=100,
            order_type=OrderType.MARKET,
            price=150
        )
        engine.execute_market_order(buy_order, current_price=150)
        
        # Then sell
        sell_order = engine.place_order(
            symbol="AAPL",
            side=OrderSide.SELL,
            quantity=100,
            order_type=OrderType.MARKET,
            price=160
        )
        report = engine.execute_market_order(sell_order, current_price=160)
        
        # Execution price should be lower due to slippage
        assert report.execution_price < 160
    
    def test_get_portfolio_value(self):
        """Test calculating portfolio value."""
        engine = ExecutionEngine(initial_capital=100_000)
        
        # Buy 100 shares @ 150
        order = engine.place_order(
            symbol="AAPL",
            side=OrderSide.BUY,
            quantity=100,
            order_type=OrderType.MARKET,
            price=150
        )
        engine.execute_market_order(order, current_price=150)
        
        # Price goes to 160
        portfolio_value = engine.get_portfolio_value({"AAPL": 160})
        # Should be approximately 100,000 + (100 * (160-150)) = 101,000 (minus commissions)
        assert portfolio_value > 100_000
    
    def test_get_total_pnl(self):
        """Test calculating total P&L."""
        engine = ExecutionEngine(initial_capital=100_000)
        
        # Buy and sell at profit
        buy_order = engine.place_order(
            symbol="AAPL",
            side=OrderSide.BUY,
            quantity=100,
            order_type=OrderType.MARKET,
            price=150
        )
        engine.execute_market_order(buy_order, current_price=150, volatility=0)
        
        sell_order = engine.place_order(
            symbol="AAPL",
            side=OrderSide.SELL,
            quantity=100,
            order_type=OrderType.MARKET,
            price=160
        )
        engine.execute_market_order(sell_order, current_price=160, volatility=0)
        
        pnl = engine.get_total_pnl({})
        assert pnl > 0  # Should have profit
    
    def test_get_return_percent(self):
        """Test calculating return percentage."""
        engine = ExecutionEngine(initial_capital=100_000)
        
        order = engine.place_order(
            symbol="AAPL",
            side=OrderSide.BUY,
            quantity=100,
            order_type=OrderType.MARKET,
            price=150
        )
        engine.execute_market_order(order, current_price=150)
        
        # Price goes to 155 (3.33% gain)
        return_pct = engine.get_return_percent({"AAPL": 155})
        # Should be positive
        assert return_pct > 0
    
    def test_execute_limit_order_buy(self):
        """Test executing a limit buy order."""
        engine = ExecutionEngine(initial_capital=100_000)
        
        order = engine.place_order(
            symbol="AAPL",
            side=OrderSide.BUY,
            quantity=100,
            order_type=OrderType.LIMIT,
            price=150
        )
        
        # Execute with price at limit using execute_order
        report = engine.execute_order(order, current_price=150)
        assert order.is_filled()
    
    def test_limit_order_not_filled(self):
        """Test limit order not filled when price is unfavorable."""
        engine = ExecutionEngine(initial_capital=100_000)
        
        order = engine.place_order(
            symbol="AAPL",
            side=OrderSide.BUY,
            quantity=100,
            order_type=OrderType.LIMIT,
            price=150
        )
        
        # Try to execute with price above limit
        report = engine._execute_limit_order(order, current_price=151)
        assert not order.is_filled()
        assert order.status == OrderStatus.PENDING
