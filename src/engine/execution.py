"""Order execution engine with realistic market conditions modeling."""

import random
from datetime import datetime
from typing import Dict, Optional, List
from dataclasses import dataclass
from .order import Order, OrderType, OrderSide, OrderStatus, ExecutionReport
from .position import PortfolioPositions


@dataclass
class SlippageModel:
    """Models realistic market slippage and spreads."""
    base_spread_bps: float = 1.0  # 1 basis point (0.01%)
    market_impact_bps: float = 0.5  # 0.5 bps per $100k traded
    volatility_multiplier: float = 1.0  # Scales with market volatility
    
    def calculate_slippage(
        self,
        quantity: float,
        price: float,
        side: OrderSide,
        volatility: float = 0.0
    ) -> float:
        """
        Calculate slippage in basis points.
        
        Args:
            quantity: Order quantity
            price: Current market price
            side: Buy or sell
            volatility: Current market volatility (0-100)
        
        Returns:
            Slippage in basis points
        """
        # Base spread
        slippage = self.base_spread_bps
        
        # Market impact increases with trade size
        trade_size_millions = (quantity * price) / 1_000_000
        market_impact = self.market_impact_bps * (trade_size_millions / 0.1)  # Impact per $100k
        slippage += market_impact
        
        # Volatility impact
        vol_impact = (volatility / 100) * self.volatility_multiplier
        slippage += vol_impact
        
        # Add randomness (0-50% variance)
        randomness = slippage * random.uniform(0, 0.5)
        slippage += randomness
        
        return slippage


class ExecutionEngine:
    """Simulates realistic order execution with market conditions."""
    
    def __init__(
        self,
        initial_capital: float = 100_000.0,
        slippage_model: Optional[SlippageModel] = None
    ):
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.positions = PortfolioPositions()
        self.slippage_model = slippage_model or SlippageModel()
        self.order_history: List[Order] = []
        self.execution_history: List[ExecutionReport] = []
        self.orders: Dict[str, Order] = {}
        self._next_order_id = 1
    
    def place_order(
        self,
        symbol: str,
        side: OrderSide,
        quantity: float,
        order_type: OrderType = OrderType.MARKET,
        price: Optional[float] = None,
        stop_price: Optional[float] = None
    ) -> Order:
        """
        Place a new order.
        
        Args:
            symbol: Trading symbol
            side: BUY or SELL
            quantity: Order quantity
            order_type: MARKET, LIMIT, STOP, etc.
            price: Limit price (for limit orders)
            stop_price: Stop price (for stop orders)
        
        Returns:
            Order object
        """
        order_id = f"ORD-{self._next_order_id}"
        self._next_order_id += 1
        
        order = Order(
            order_id=order_id,
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=quantity,
            price=price or 0.0,
            stop_price=stop_price,
            limit_price=price
        )
        
        self.orders[order_id] = order
        return order
    
    def execute_market_order(
        self,
        order: Order,
        current_price: float,
        volatility: float = 0.0
    ) -> ExecutionReport:
        """
        Execute a market order immediately.
        
        Args:
            order: Order to execute
            current_price: Current market price
            volatility: Current volatility for slippage calculation
        
        Returns:
            ExecutionReport
        """
        if order.order_type != OrderType.MARKET:
            raise ValueError(f"Expected MARKET order, got {order.order_type}")
        
        # Calculate slippage
        slippage_bps = self.slippage_model.calculate_slippage(
            quantity=order.quantity,
            price=current_price,
            side=order.side,
            volatility=volatility
        )
        
        # Apply slippage to execution price
        slippage_multiplier = 1 + (slippage_bps / 10000)
        if order.side == OrderSide.BUY:
            execution_price = current_price * slippage_multiplier  # Worse price when buying
        else:
            execution_price = current_price / slippage_multiplier  # Worse price when selling
        
        # Calculate commission (flat 0.1%)
        commission = order.quantity * execution_price * 0.001
        
        # Check if we have sufficient funds (for buys)
        if order.side == OrderSide.BUY:
            total_cost = order.quantity * execution_price + commission
            if total_cost > self.cash:
                order.status = OrderStatus.REJECTED
                return ExecutionReport(
                    order=order,
                    execution_price=0.0,
                    quantity_filled=0.0,
                    slippage=0.0,
                    latency_ms=random.uniform(50, 150)
                )
        
        # Fill the order
        order.fill(order.quantity, execution_price, commission)
        
        # Update cash
        if order.side == OrderSide.BUY:
            self.cash -= (order.quantity * execution_price + commission)
        else:
            self.cash += (order.quantity * execution_price - commission)
        
        # Add to positions
        self.positions.add_trade(order, execution_price)
        
        # Record execution
        execution_report = ExecutionReport(
            order=order,
            execution_price=execution_price,
            quantity_filled=order.quantity,
            slippage=slippage_bps,
            latency_ms=random.uniform(50, 150)
        )
        
        self.execution_history.append(execution_report)
        self.order_history.append(order)
        
        return execution_report
    
    def execute_order(
        self,
        order: Order,
        current_price: float,
        volatility: float = 0.0
    ) -> ExecutionReport:
        """
        Execute an order (handles different order types).
        
        Args:
            order: Order to execute
            current_price: Current market price
            volatility: Current volatility
        
        Returns:
            ExecutionReport
        """
        if order.order_type == OrderType.MARKET:
            return self.execute_market_order(order, current_price, volatility)
        elif order.order_type == OrderType.LIMIT:
            return self._execute_limit_order(order, current_price, volatility)
        else:
            raise NotImplementedError(f"Order type {order.order_type} not yet implemented")
    
    def _execute_limit_order(
        self,
        order: Order,
        current_price: float,
        volatility: float = 0.0
    ) -> ExecutionReport:
        """Execute a limit order (only if price is favorable)."""
        if order.side == OrderSide.BUY and current_price <= order.limit_price:
            # Can execute
            execution_price = min(current_price, order.limit_price)
        elif order.side == OrderSide.SELL and current_price >= order.limit_price:
            # Can execute
            execution_price = max(current_price, order.limit_price)
        else:
            # Cannot execute at limit price
            order.status = OrderStatus.PENDING
            return ExecutionReport(
                order=order,
                execution_price=0.0,
                quantity_filled=0.0,
                slippage=0.0,
                latency_ms=0.0
            )
        
        # Execute at limit price (no slippage on limit orders)
        commission = order.quantity * execution_price * 0.001
        
        # Check funds
        if order.side == OrderSide.BUY:
            total_cost = order.quantity * execution_price + commission
            if total_cost > self.cash:
                order.status = OrderStatus.REJECTED
                return ExecutionReport(
                    order=order,
                    execution_price=0.0,
                    quantity_filled=0.0,
                    slippage=0.0,
                    latency_ms=0.0
                )
        
        # Fill order
        order.fill(order.quantity, execution_price, commission)
        
        # Update cash
        if order.side == OrderSide.BUY:
            self.cash -= (order.quantity * execution_price + commission)
        else:
            self.cash += (order.quantity * execution_price - commission)
        
        # Add to positions
        self.positions.add_trade(order, execution_price)
        
        execution_report = ExecutionReport(
            order=order,
            execution_price=execution_price,
            quantity_filled=order.quantity,
            slippage=0.0,  # No slippage on limit orders
            latency_ms=random.uniform(100, 200)
        )
        
        self.execution_history.append(execution_report)
        self.order_history.append(order)
        
        return execution_report
    
    def get_portfolio_value(self, prices: Dict[str, float]) -> float:
        """Get total portfolio value (cash + positions)."""
        position_value = self.positions.get_total_exposure(prices)
        return self.cash + position_value
    
    def get_total_pnl(self, prices: Dict[str, float]) -> float:
        """Get total P&L (realized + unrealized)."""
        realized = self.positions.get_total_realized_pnl()
        unrealized = self.positions.get_total_unrealized_pnl(prices)
        return realized + unrealized
    
    def get_return_percent(self, prices: Dict[str, float]) -> float:
        """Get total return as a percentage."""
        portfolio_value = self.get_portfolio_value(prices)
        if self.initial_capital == 0:
            return 0.0
        return ((portfolio_value - self.initial_capital) / self.initial_capital) * 100
