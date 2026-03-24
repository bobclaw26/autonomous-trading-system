"""Stop loss and take profit management."""

from typing import Optional, Tuple


class StopLossManager:
    """Manage stop loss and take profit levels."""
    
    def __init__(self, stop_loss_pct: float = 0.02, take_profit_pct: float = 0.05):
        """
        Initialize stop loss manager.
        
        Args:
            stop_loss_pct: Stop loss percentage (0.02 = 2%)
            take_profit_pct: Take profit percentage (0.05 = 5%)
        """
        self.stop_loss_pct = stop_loss_pct
        self.take_profit_pct = take_profit_pct
    
    def calculate_levels(self, entry_price: float, 
                        side: str = "BUY") -> Tuple[float, float]:
        """
        Calculate stop loss and take profit levels.
        
        Args:
            entry_price: Entry price
            side: BUY or SELL
        
        Returns:
            Tuple of (stop_loss, take_profit)
        """
        if side == "BUY":
            stop_loss = entry_price * (1 - self.stop_loss_pct)
            take_profit = entry_price * (1 + self.take_profit_pct)
        else:  # SELL
            stop_loss = entry_price * (1 + self.stop_loss_pct)
            take_profit = entry_price * (1 - self.take_profit_pct)
        
        return stop_loss, take_profit
    
    def trailing_stop(self, entry_price: float, current_price: float,
                     trailing_pct: float = 0.02) -> float:
        """
        Calculate trailing stop level.
        
        Args:
            entry_price: Entry price
            current_price: Current price
            trailing_pct: Trailing stop percentage
        
        Returns:
            Trailing stop level
        """
        if current_price > entry_price:
            # Long position - trailing stop below peak
            trailing_stop = current_price * (1 - trailing_pct)
        else:
            # Short position - trailing stop above peak
            trailing_stop = current_price * (1 + trailing_pct)
        
        return trailing_stop
    
    def atr_stop(self, entry_price: float, atr_value: float, 
                multiplier: float = 2.0) -> float:
        """
        Calculate ATR-based stop loss.
        
        Args:
            entry_price: Entry price
            atr_value: Average True Range value
            multiplier: ATR multiplier
        
        Returns:
            Stop loss level
        """
        stop_loss = entry_price - (atr_value * multiplier)
        return max(stop_loss, 0.0)  # Ensure positive
    
    def check_stop_loss(self, entry_price: float, current_price: float,
                       stop_loss: float) -> bool:
        """
        Check if stop loss is triggered.
        
        Args:
            entry_price: Entry price
            current_price: Current price
            stop_loss: Stop loss level
        
        Returns:
            True if stop loss is triggered
        """
        if entry_price > stop_loss:
            # Long position
            return current_price <= stop_loss
        else:
            # Short position
            return current_price >= stop_loss
    
    def check_take_profit(self, entry_price: float, current_price: float,
                         take_profit: float) -> bool:
        """
        Check if take profit is triggered.
        
        Args:
            entry_price: Entry price
            current_price: Current price
            take_profit: Take profit level
        
        Returns:
            True if take profit is triggered
        """
        if entry_price < take_profit:
            # Long position
            return current_price >= take_profit
        else:
            # Short position
            return current_price <= take_profit
