"""Order management and execution types for the trading engine."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
from decimal import Decimal


class OrderType(Enum):
    """Order types supported by the trading engine."""
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"


class OrderSide(Enum):
    """Buy or sell side."""
    BUY = "buy"
    SELL = "sell"


class OrderStatus(Enum):
    """Order execution status."""
    PENDING = "pending"
    FILLED = "filled"
    PARTIAL = "partial"
    CANCELLED = "cancelled"
    REJECTED = "rejected"


@dataclass
class Order:
    """Represents a trading order."""
    order_id: str
    symbol: str
    side: OrderSide
    order_type: OrderType
    quantity: float
    price: float
    timestamp: datetime = field(default_factory=datetime.utcnow)
    status: OrderStatus = OrderStatus.PENDING
    filled_quantity: float = 0.0
    fill_price: float = 0.0
    commission: float = 0.0
    stop_price: Optional[float] = None
    limit_price: Optional[float] = None
    notes: str = ""

    def __post_init__(self):
        """Validate order parameters."""
        if self.quantity <= 0:
            raise ValueError("Quantity must be positive")
        if self.price < 0:
            raise ValueError("Price cannot be negative")
        if self.side not in OrderSide:
            raise ValueError(f"Invalid order side: {self.side}")
        if self.order_type not in OrderType:
            raise ValueError(f"Invalid order type: {self.order_type}")

    def is_filled(self) -> bool:
        """Check if order is fully filled."""
        return self.status == OrderStatus.FILLED

    def is_open(self) -> bool:
        """Check if order is still open (can be filled)."""
        return self.status in (OrderStatus.PENDING, OrderStatus.PARTIAL)

    def get_remaining_quantity(self) -> float:
        """Get quantity remaining to be filled."""
        return self.quantity - self.filled_quantity

    def get_total_cost(self) -> float:
        """Get total cost including commission."""
        return self.filled_quantity * self.fill_price + self.commission

    def get_execution_price(self) -> float:
        """Get average execution price including commission."""
        if self.filled_quantity == 0:
            return 0.0
        total_cost = self.get_total_cost()
        return total_cost / self.filled_quantity if self.filled_quantity > 0 else 0.0

    def fill(self, fill_quantity: float, fill_price: float, commission: float = 0.0):
        """Record a partial or full fill of the order."""
        if fill_quantity > self.get_remaining_quantity():
            raise ValueError(f"Fill quantity {fill_quantity} exceeds remaining {self.get_remaining_quantity()}")
        
        # Calculate weighted average fill price
        total_filled_value = (self.filled_quantity * self.fill_price) + (fill_quantity * fill_price)
        new_filled_quantity = self.filled_quantity + fill_quantity
        self.fill_price = total_filled_value / new_filled_quantity
        
        self.filled_quantity = new_filled_quantity
        self.commission += commission
        
        # Update status
        if self.filled_quantity >= self.quantity:
            self.status = OrderStatus.FILLED
        else:
            self.status = OrderStatus.PARTIAL

    def cancel(self):
        """Cancel the order."""
        if not self.is_open():
            raise ValueError(f"Cannot cancel order with status {self.status}")
        self.status = OrderStatus.CANCELLED


@dataclass
class ExecutionReport:
    """Report from order execution."""
    order: Order
    execution_price: float
    quantity_filled: float
    slippage: float  # In basis points (bps)
    latency_ms: float
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def get_slippage_amount(self) -> float:
        """Get slippage amount in currency units."""
        return (self.slippage / 10000) * self.execution_price * self.quantity_filled
