"""Risk limit enforcement."""

from typing import Dict, Tuple


class RiskLimits:
    """Enforce portfolio-level risk limits."""
    
    def __init__(self, initial_capital: float, max_drawdown: float = 0.20,
                 max_daily_loss: float = 0.05):
        """
        Initialize risk limits.
        
        Args:
            initial_capital: Starting portfolio value
            max_drawdown: Maximum drawdown allowed (0.20 = 20%)
            max_daily_loss: Maximum daily loss allowed (0.05 = 5%)
        """
        self.initial_capital = initial_capital
        self.max_drawdown = max_drawdown
        self.max_daily_loss = max_daily_loss
        self.peak_capital = initial_capital
        self.daily_start_capital = initial_capital
    
    def check_drawdown(self, current_capital: float) -> Tuple[bool, float]:
        """
        Check if portfolio exceeds max drawdown.
        
        Args:
            current_capital: Current portfolio value
        
        Returns:
            Tuple of (is_valid, drawdown_percent)
        """
        if current_capital > self.peak_capital:
            self.peak_capital = current_capital
        
        drawdown = (self.peak_capital - current_capital) / self.peak_capital
        is_valid = drawdown <= self.max_drawdown
        
        return is_valid, drawdown
    
    def check_daily_loss(self, current_capital: float) -> Tuple[bool, float]:
        """
        Check if daily loss exceeds limit.
        
        Args:
            current_capital: Current portfolio value
        
        Returns:
            Tuple of (is_valid, daily_loss_percent)
        """
        daily_loss = (self.daily_start_capital - current_capital) / self.daily_start_capital
        is_valid = daily_loss <= self.max_daily_loss
        
        return is_valid, daily_loss
    
    def check_max_position(self, position_value: float, 
                          portfolio_value: float) -> Tuple[bool, float]:
        """
        Check if position exceeds max position size.
        
        Args:
            position_value: Value of the position
            portfolio_value: Total portfolio value
        
        Returns:
            Tuple of (is_valid, position_percent)
        """
        position_percent = position_value / portfolio_value if portfolio_value > 0 else 0
        max_position = 0.05  # 5% max per position
        is_valid = position_percent <= max_position
        
        return is_valid, position_percent
    
    def should_stop_trading(self, current_capital: float) -> bool:
        """
        Determine if should stop trading.
        
        Args:
            current_capital: Current portfolio value
        
        Returns:
            True if trading should be halted
        """
        drawdown_valid, _ = self.check_drawdown(current_capital)
        daily_valid, _ = self.check_daily_loss(current_capital)
        
        return not (drawdown_valid and daily_valid)
    
    def reset_daily_limits(self, current_capital: float):
        """Reset daily loss counter."""
        self.daily_start_capital = current_capital
