"""Position tracking and management for the trading engine."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional
from .order import Order, OrderSide


@dataclass
class Position:
    """Represents a trading position in a single symbol."""
    symbol: str
    quantity: float = 0.0
    entry_price: float = 0.0
    current_price: float = 0.0
    entry_time: Optional[datetime] = None
    exit_time: Optional[datetime] = None
    trades: List[Order] = field(default_factory=list)
    
    def __post_init__(self):
        """Validate position."""
        if self.quantity < 0:
            raise ValueError("Quantity cannot be negative")

    def is_open(self) -> bool:
        """Check if position is open."""
        return self.quantity > 0

    def is_long(self) -> bool:
        """Check if position is a long."""
        return self.quantity > 0

    def add_trade(self, order: Order, execution_price: float):
        """Add a trade to the position."""
        if order.side == OrderSide.BUY:
            # Calculate new entry price (weighted average)
            if self.quantity > 0:
                total_value = (self.quantity * self.entry_price) + (order.filled_quantity * execution_price)
                self.quantity += order.filled_quantity
                self.entry_price = total_value / self.quantity
            else:
                self.quantity = order.filled_quantity
                self.entry_price = execution_price
                self.entry_time = order.timestamp
        
        elif order.side == OrderSide.SELL:
            # Reduce position
            if self.quantity <= 0:
                raise ValueError("Cannot sell without open position")
            if order.filled_quantity > self.quantity:
                raise ValueError(f"Cannot sell {order.filled_quantity} units, only {self.quantity} open")
            
            self.quantity -= order.filled_quantity
            
            if self.quantity == 0:
                self.exit_time = order.timestamp
        
        self.trades.append(order)

    def get_unrealized_pnl(self, current_price: float) -> float:
        """Get unrealized P&L."""
        if self.quantity == 0:
            return 0.0
        self.current_price = current_price
        return self.quantity * (current_price - self.entry_price)

    def get_unrealized_pnl_percent(self, current_price: float) -> float:
        """Get unrealized P&L as a percentage."""
        if self.entry_price == 0:
            return 0.0
        return ((current_price - self.entry_price) / self.entry_price) * 100

    def get_realized_pnl(self) -> float:
        """Calculate realized P&L from closed trades."""
        realized_pnl = 0.0
        buy_quantity = 0.0
        buy_cost = 0.0
        
        for trade in self.trades:
            if trade.side == OrderSide.BUY:
                buy_quantity += trade.filled_quantity
                buy_cost += trade.get_total_cost()
            else:  # SELL
                # Match sell against buys (FIFO)
                sell_revenue = trade.filled_quantity * trade.fill_price - trade.commission
                # Simple P&L: revenue - cost
                if buy_quantity > 0:
                    avg_cost = buy_cost / buy_quantity
                    realized_pnl += (trade.fill_price - avg_cost) * trade.filled_quantity - trade.commission
                    buy_quantity -= trade.filled_quantity
                    buy_cost -= trade.filled_quantity * avg_cost
        
        return realized_pnl

    def __str__(self) -> str:
        return f"Position({self.symbol}, qty={self.quantity}, entry_price={self.entry_price:.2f})"


class PortfolioPositions:
    """Manages all positions in the portfolio."""
    
    def __init__(self):
        self.positions: Dict[str, Position] = {}
    
    def add_position(self, symbol: str) -> Position:
        """Add or get a position."""
        if symbol not in self.positions:
            self.positions[symbol] = Position(symbol=symbol)
        return self.positions[symbol]
    
    def get_position(self, symbol: str) -> Optional[Position]:
        """Get a position."""
        return self.positions.get(symbol)
    
    def add_trade(self, order: Order, execution_price: float):
        """Add a trade to the appropriate position."""
        position = self.add_position(order.symbol)
        position.add_trade(order, execution_price)
    
    def get_open_positions(self) -> List[Position]:
        """Get all open positions."""
        return [p for p in self.positions.values() if p.is_open()]
    
    def get_closed_positions(self) -> List[Position]:
        """Get all closed positions."""
        return [p for p in self.positions.values() if not p.is_open()]
    
    def get_total_unrealized_pnl(self, prices: Dict[str, float]) -> float:
        """Get total unrealized P&L across all positions."""
        total = 0.0
        for symbol, position in self.positions.items():
            if position.is_open() and symbol in prices:
                total += position.get_unrealized_pnl(prices[symbol])
        return total
    
    def get_total_realized_pnl(self) -> float:
        """Get total realized P&L across all positions."""
        return sum(p.get_realized_pnl() for p in self.positions.values())
    
    def get_total_exposure(self, prices: Dict[str, float]) -> float:
        """Get total portfolio exposure in dollars."""
        total = 0.0
        for symbol, position in self.positions.items():
            if position.is_open() and symbol in prices:
                total += position.quantity * prices[symbol]
        return total
