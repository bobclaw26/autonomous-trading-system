"""Base strategy interface for all trading strategies."""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, Optional


class Signal(Enum):
    """Trading signal enumeration."""
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"


class BaseStrategy(ABC):
    """Abstract base class for all trading strategies."""
    
    def __init__(self, name: str):
        self.name = name
        self.signals_generated = 0
        self.buy_signals = 0
        self.sell_signals = 0
    
    @abstractmethod
    def generate_signal(self, prices: Dict[str, float], **kwargs) -> Signal:
        """
        Generate a trading signal based on market conditions.
        
        Args:
            prices: Dictionary of current prices by symbol
            **kwargs: Additional context (history, volume, etc.)
        
        Returns:
            Trading signal (BUY, SELL, or HOLD)
        """
        pass
    
    def record_signal(self, signal: Signal):
        """Record a generated signal for analytics."""
        self.signals_generated += 1
        
        if signal == Signal.BUY:
            self.buy_signals += 1
        elif signal == Signal.SELL:
            self.sell_signals += 1
    
    def get_signal_ratio(self) -> Dict[str, float]:
        """Get ratio of different signal types."""
        if self.signals_generated == 0:
            return {"buy": 0, "sell": 0, "hold": 0}
        
        buy_ratio = self.buy_signals / self.signals_generated
        sell_ratio = self.sell_signals / self.signals_generated
        hold_ratio = 1 - buy_ratio - sell_ratio
        
        return {
            "buy": buy_ratio,
            "sell": sell_ratio,
            "hold": hold_ratio
        }
    
    def reset_signals(self):
        """Reset signal counters."""
        self.signals_generated = 0
        self.buy_signals = 0
        self.sell_signals = 0
    
    def __str__(self) -> str:
        return f"{self.name}Strategy"
