"""Position sizing strategies."""

import math
from typing import Dict


class PositionSizer:
    """Calculate position size based on risk parameters."""
    
    def __init__(self, portfolio_value: float, risk_per_trade: float = 0.02):
        """
        Initialize position sizer.
        
        Args:
            portfolio_value: Total portfolio value
            risk_per_trade: Risk per trade as decimal (0.02 = 2%)
        """
        self.portfolio_value = portfolio_value
        self.risk_per_trade = risk_per_trade
    
    def fixed_fractional(self, entry_price: float, stop_price: float) -> float:
        """
        Calculate position size using fixed fractional method.
        
        Args:
            entry_price: Entry price for the trade
            stop_price: Stop loss price
        
        Returns:
            Position size in shares
        """
        if entry_price <= stop_price:
            return 0.0
        
        # Risk amount in dollars
        risk_amount = self.portfolio_value * self.risk_per_trade
        
        # Price risk per share
        price_risk = abs(entry_price - stop_price)
        
        # Position size
        position_size = risk_amount / price_risk
        
        return position_size
    
    def kelly_criterion(self, win_rate: float, avg_win: float, 
                       avg_loss: float) -> float:
        """
        Calculate position size using Kelly Criterion.
        
        Args:
            win_rate: Win rate as decimal (0.5 = 50%)
            avg_win: Average win amount
            avg_loss: Average loss amount
        
        Returns:
            Fraction of portfolio to risk (0-1)
        """
        if avg_loss == 0 or win_rate == 0:
            return 0.0
        
        # Kelly: f = (bp - q) / b where:
        # b = ratio of win to loss
        # p = win rate
        # q = loss rate
        
        b = avg_win / avg_loss
        p = win_rate
        q = 1 - win_rate
        
        kelly_fraction = (b * p - q) / b
        
        # Conservative: use 25% of Kelly to reduce drawdown
        return max(0, min(1, kelly_fraction * 0.25))
    
    def dynamic_sizing(self, volatility: float, base_size: float) -> float:
        """
        Adjust position size based on market volatility.
        
        Args:
            volatility: Current market volatility
            base_size: Base position size
        
        Returns:
            Adjusted position size
        """
        # Higher volatility = smaller position
        volatility_factor = 1.0 / (1.0 + volatility)
        return base_size * volatility_factor
