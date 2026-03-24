"""Tests for order management module."""

import pytest
from datetime import datetime
from src.engine.order import Order, OrderType, OrderSide, OrderStatus


class TestOrder:
    """Test Order class."""
    
    def test_create_market_order(self):
        """Test creating a market order."""
        order = Order(
            order_id="ORD-001",
            symbol="AAPL",
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            quantity=100.0,
            price=150.0
        )
        assert order.symbol == "AAPL"
        assert order.quantity == 100.0
        assert order.status == OrderStatus.PENDING
    
    def test_invalid_quantity(self):
        """Test that invalid quantity raises error."""
        with pytest.raises(ValueError):
            Order(
                order_id="ORD-001",
                symbol="AAPL",
                side=OrderSide.BUY,
                order_type=OrderType.MARKET,
                quantity=-100.0,
                price=150.0
            )
    
    def test_invalid_price(self):
        """Test that negative price raises error."""
        with pytest.raises(ValueError):
            Order(
                order_id="ORD-001",
                symbol="AAPL",
                side=OrderSide.BUY,
                order_type=OrderType.MARKET,
                quantity=100.0,
                price=-150.0
            )
    
    def test_order_fill(self):
        """Test filling an order."""
        order = Order(
            order_id="ORD-001",
            symbol="AAPL",
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            quantity=100.0,
            price=150.0
        )
        
        order.fill(50.0, 150.5, commission=7.5)
        assert order.filled_quantity == 50.0
        assert order.fill_price == 150.5
        assert order.status == OrderStatus.PARTIAL
        assert order.commission == 7.5
    
    def test_order_full_fill(self):
        """Test fully filling an order."""
        order = Order(
            order_id="ORD-001",
            symbol="AAPL",
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            quantity=100.0,
            price=150.0
        )
        
        order.fill(100.0, 150.5, commission=15.0)
        assert order.is_filled()
        assert order.filled_quantity == 100.0
    
    def test_order_weighted_average_fill_price(self):
        """Test weighted average fill price with multiple fills."""
        order = Order(
            order_id="ORD-001",
            symbol="AAPL",
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            quantity=200.0,
            price=150.0
        )
        
        # First fill: 100 @ 150
        order.fill(100.0, 150.0, commission=15.0)
        assert order.fill_price == 150.0
        
        # Second fill: 100 @ 151
        order.fill(100.0, 151.0, commission=15.0)
        # Weighted average: (100*150 + 100*151) / 200 = 150.5
        assert abs(order.fill_price - 150.5) < 0.01
    
    def test_order_cancel(self):
        """Test canceling an order."""
        order = Order(
            order_id="ORD-001",
            symbol="AAPL",
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            quantity=100.0,
            price=150.0
        )
        
        order.cancel()
        assert order.status == OrderStatus.CANCELLED
    
    def test_cannot_cancel_filled_order(self):
        """Test that filled orders cannot be canceled."""
        order = Order(
            order_id="ORD-001",
            symbol="AAPL",
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            quantity=100.0,
            price=150.0
        )
        
        order.fill(100.0, 150.0)
        with pytest.raises(ValueError):
            order.cancel()
    
    def test_get_remaining_quantity(self):
        """Test getting remaining quantity."""
        order = Order(
            order_id="ORD-001",
            symbol="AAPL",
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            quantity=100.0,
            price=150.0
        )
        
        assert order.get_remaining_quantity() == 100.0
        order.fill(30.0, 150.0)
        assert order.get_remaining_quantity() == 70.0
    
    def test_get_total_cost(self):
        """Test getting total cost including commission."""
        order = Order(
            order_id="ORD-001",
            symbol="AAPL",
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            quantity=100.0,
            price=150.0
        )
        
        order.fill(100.0, 150.0, commission=15.0)
        total_cost = order.get_total_cost()
        assert total_cost == 100.0 * 150.0 + 15.0
    
    def test_get_execution_price(self):
        """Test getting execution price with commission."""
        order = Order(
            order_id="ORD-001",
            symbol="AAPL",
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            quantity=100.0,
            price=150.0
        )
        
        order.fill(100.0, 150.0, commission=15.0)
        exec_price = order.get_execution_price()
        # (100 * 150 + 15) / 100 = 150.15
        assert abs(exec_price - 150.15) < 0.01
