"""Data models for market data."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class OHLCV:
    """Open, High, Low, Close, Volume data."""
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int
    symbol: str = ""
    
    def __post_init__(self):
        if self.close <= 0:
            raise ValueError("Close price must be positive")
        if self.volume < 0:
            raise ValueError("Volume cannot be negative")


@dataclass
class Tick:
    """Individual trade tick."""
    timestamp: datetime
    price: float
    quantity: float
    symbol: str = ""
    side: str = "BUY"


@dataclass
class Quote:
    """Real-time price quote."""
    timestamp: datetime
    symbol: str
    bid: float
    ask: float
    last: float
    volume: int = 0
    
    def get_mid_price(self) -> float:
        """Get mid price between bid and ask."""
        return (self.bid + self.ask) / 2
