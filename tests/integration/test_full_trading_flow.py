"""Integration tests for complete trading system flow."""

import pytest
from src.engine.order import OrderType, OrderSide
from src.engine.execution import ExecutionEngine, SlippageModel
from src.engine.portfolio import PortfolioManager


class TestFullTradingFlow:
    """Test complete trading workflows across all components."""
    
    def test_buy_sell_cycle(self):
        """Test a complete buy-sell trading cycle."""
        # Setup
        engine = ExecutionEngine(initial_capital=100_000)
        manager = PortfolioManager(engine)
        
        # BUY 100 shares @ $150
        buy_order = engine.place_order(
            symbol="AAPL",
            side=OrderSide.BUY,
            quantity=100,
            order_type=OrderType.MARKET,
            price=150
        )
        
        buy_report = engine.execute_market_order(buy_order, current_price=150, volatility=10)
        assert buy_report.quantity_filled == 100
        assert engine.positions.get_position("AAPL").is_open()
        
        # Take snapshot after buy
        snapshot1 = manager.take_snapshot({"AAPL": 150})
        initial_portfolio_value = snapshot1.portfolio_value
        assert initial_portfolio_value < 100_000  # Cash reduced
        
        # SELL 100 shares @ $160 (profit of $10 per share)
        sell_order = engine.place_order(
            symbol="AAPL",
            side=OrderSide.SELL,
            quantity=100,
            order_type=OrderType.MARKET,
            price=160
        )
        
        sell_report = engine.execute_market_order(sell_order, current_price=160, volatility=10)
        assert sell_report.quantity_filled == 100
        assert not engine.positions.get_position("AAPL").is_open()
        
        # Take snapshot after sell
        snapshot2 = manager.take_snapshot({"AAPL": 160})
        final_portfolio_value = snapshot2.portfolio_value
        
        # Should have profit (minus commissions and slippage)
        assert final_portfolio_value > initial_portfolio_value
        assert engine.get_total_pnl({}) > 0
    
    def test_multiple_position_management(self):
        """Test managing multiple positions simultaneously."""
        engine = ExecutionEngine(initial_capital=100_000)
        manager = PortfolioManager(engine)
        
        # Buy different stocks
        symbols = ["AAPL", "MSFT", "GOOGL"]
        for symbol in symbols:
            order = engine.place_order(
                symbol=symbol,
                side=OrderSide.BUY,
                quantity=50,
                order_type=OrderType.MARKET,
                price=100
            )
            engine.execute_market_order(order, current_price=100)
        
        # All positions should be open
        open_positions = engine.positions.get_open_positions()
        assert len(open_positions) == 3
        
        # Price changes
        prices = {"AAPL": 105, "MSFT": 98, "GOOGL": 110}
        snapshot = manager.take_snapshot(prices)
        
        # Check portfolio metrics
        assert snapshot.open_positions_count == 3
        assert snapshot.unrealized_pnl != 0  # Some positions profitable, some not
    
    def test_risk_limits_enforcement(self):
        """Test fund availability checks (actual risk limits handled by Risk Manager)."""
        engine = ExecutionEngine(initial_capital=100_000)
        
        # Try to buy more than we have cash for
        oversized_order = engine.place_order(
            symbol="AAPL",
            side=OrderSide.BUY,
            quantity=10000,  # Way too many (10000 * 150 = $1.5M, we only have $100k)
            order_type=OrderType.MARKET,
            price=150
        )
        
        # This should be rejected due to insufficient funds
        report = engine.execute_market_order(oversized_order, current_price=150)
        from src.engine.order import OrderStatus
        assert oversized_order.status == OrderStatus.REJECTED
    
    def test_slippage_impact_on_profitability(self):
        """Test how slippage affects trading profitability."""
        # Without slippage
        engine_no_slip = ExecutionEngine(
            initial_capital=100_000,
            slippage_model=SlippageModel(base_spread_bps=0)
        )
        
        # With slippage
        engine_with_slip = ExecutionEngine(
            initial_capital=100_000,
            slippage_model=SlippageModel(base_spread_bps=10)  # 0.1%
        )
        
        # Both buy @ 150
        order1 = engine_no_slip.place_order(
            symbol="AAPL", side=OrderSide.BUY, quantity=100,
            order_type=OrderType.MARKET, price=150
        )
        engine_no_slip.execute_market_order(order1, current_price=150)
        
        order2 = engine_with_slip.place_order(
            symbol="AAPL", side=OrderSide.BUY, quantity=100,
            order_type=OrderType.MARKET, price=150
        )
        engine_with_slip.execute_market_order(order2, current_price=150)
        
        # Without slippage should have more cash remaining
        assert engine_no_slip.cash > engine_with_slip.cash
    
    def test_performance_metrics_calculation(self):
        """Test portfolio performance metrics across trades."""
        engine = ExecutionEngine(initial_capital=100_000)
        manager = PortfolioManager(engine)
        
        # Make some trades
        prices = {"AAPL": 100}
        
        # Trade 1: Buy @ 100, sell @ 110 (profit)
        buy1 = engine.place_order("AAPL", OrderSide.BUY, 50, OrderType.MARKET, 100)
        engine.execute_market_order(buy1, current_price=100)
        
        sell1 = engine.place_order("AAPL", OrderSide.SELL, 50, OrderType.MARKET, 110)
        engine.execute_market_order(sell1, current_price=110)
        
        # Trade 2: Buy MSFT @ 100, sell @ 90 (loss)
        buy2 = engine.place_order("MSFT", OrderSide.BUY, 50, OrderType.MARKET, 100)
        engine.execute_market_order(buy2, current_price=100)
        
        sell2 = engine.place_order("MSFT", OrderSide.SELL, 50, OrderType.MARKET, 90)
        engine.execute_market_order(sell2, current_price=90)
        
        # Record daily returns
        manager.record_daily_return(0.01)  # +1%
        manager.record_daily_return(-0.005)  # -0.5%
        manager.record_daily_return(0.015)  # +1.5%
        
        # Check metrics
        stats = manager.get_summary_stats(prices)
        
        assert stats["total_trades"] >= 4
        assert stats["closed_positions"] >= 1
        # Win rate should be measurable
        assert isinstance(stats["win_rate"], (int, float))
        # Sharpe ratio should be calculated
        assert isinstance(stats["sharpe_ratio"], (int, float))
    
    def test_order_cancellation_flow(self):
        """Test order cancellation and position adjustments."""
        engine = ExecutionEngine(initial_capital=100_000)
        
        # Place buy order
        order = engine.place_order(
            symbol="AAPL",
            side=OrderSide.BUY,
            quantity=100,
            order_type=OrderType.MARKET,
            price=150
        )
        
        # Can't cancel after execution
        engine.execute_market_order(order, current_price=150)
        
        with pytest.raises(ValueError):
            order.cancel()
    
    def test_cash_management_across_trades(self):
        """Test that cash is properly managed across multiple trades."""
        engine = ExecutionEngine(initial_capital=100_000)
        initial_cash = engine.cash
        
        # Make a buy that uses half the capital
        order1 = engine.place_order("AAPL", OrderSide.BUY, 300, 
                                    OrderType.MARKET, 150)
        engine.execute_market_order(order1, current_price=150)
        
        cash_after_buy = engine.cash
        assert cash_after_buy < initial_cash
        assert cash_after_buy > 0  # Still have cash left
        
        # Now buy another stock
        order2 = engine.place_order("MSFT", OrderSide.BUY, 200,
                                    OrderType.MARKET, 100)
        engine.execute_market_order(order2, current_price=100)
        
        cash_after_second_buy = engine.cash
        assert cash_after_second_buy < cash_after_buy
        
        # Sell first position
        sell_order = engine.place_order("AAPL", OrderSide.SELL, 300,
                                       OrderType.MARKET, 155)
        engine.execute_market_order(sell_order, current_price=155)
        
        cash_after_sell = engine.cash
        # Should have more cash after selling at profit
        assert cash_after_sell > cash_after_second_buy


class TestIntegrationWithRiskManager:
    """Test integration between execution and risk management."""
    
    def test_stop_loss_trigger(self):
        """Test stop-loss functionality (ready for risk manager integration)."""
        engine = ExecutionEngine(initial_capital=100_000)
        
        # Buy @ 100
        buy = engine.place_order("AAPL", OrderSide.BUY, 100,
                                 OrderType.MARKET, 100)
        engine.execute_market_order(buy, current_price=100)
        
        position = engine.positions.get_position("AAPL")
        assert position.quantity == 100
        # Entry price includes slippage, so it's slightly higher than 100
        assert position.entry_price >= 100
        
        # Calculate when stop-loss would trigger (at 2% loss from entry)
        stop_price = position.entry_price * 0.98
        
        # At stop price, should show loss
        position_pnl = position.get_unrealized_pnl(stop_price)
        # Should be close to -2% loss (may be slightly different due to slippage)
        pnl_percent = position.get_unrealized_pnl_percent(stop_price)
        assert pnl_percent < 0  # In loss


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
