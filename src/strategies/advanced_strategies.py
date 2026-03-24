"""Advanced trading strategies for Phase 2."""

from typing import Dict, List, Optional
from dataclasses import dataclass
from src.strategies.base_strategy import BaseStrategy, Signal


@dataclass
class StrategyConfig:
    """Configuration for strategies."""
    fast_period: int = 12
    slow_period: int = 26
    signal_period: int = 9
    rsi_period: int = 14
    rsi_overbought: int = 70
    rsi_oversold: int = 30
    bb_period: int = 20
    bb_std_dev: float = 2.0
    volume_period: int = 20


class RSIStrategy(BaseStrategy):
    """Relative Strength Index (RSI) mean reversion strategy."""
    
    def __init__(self, config: StrategyConfig = None):
        super().__init__("RSI")
        self.config = config or StrategyConfig()
    
    def generate_signal(self, prices: Dict[str, float], **kwargs) -> Signal:
        """Generate signal based on RSI."""
        symbol = kwargs.get("symbol", "AAPL")
        price = prices.get(symbol, 0)
        history = kwargs.get("history", [])
        
        if len(history) < self.config.rsi_period:
            return Signal.HOLD
        
        # Calculate RSI
        gains = []
        losses = []
        
        for i in range(1, len(history[-self.config.rsi_period:]) + 1):
            change = history[-self.config.rsi_period + i] - history[-self.config.rsi_period + i - 1]
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))
        
        avg_gain = sum(gains) / self.config.rsi_period if gains else 0
        avg_loss = sum(losses) / self.config.rsi_period if losses else 1
        
        rs = avg_gain / avg_loss if avg_loss != 0 else 0
        rsi = 100 - (100 / (1 + rs))
        
        # Generate signals
        if rsi < self.config.rsi_oversold:
            return Signal.BUY
        elif rsi > self.config.rsi_overbought:
            return Signal.SELL
        else:
            return Signal.HOLD


class MACDStrategy(BaseStrategy):
    """MACD (Moving Average Convergence Divergence) trend-following strategy."""
    
    def __init__(self, config: StrategyConfig = None):
        super().__init__("MACD")
        self.config = config or StrategyConfig()
    
    def generate_signal(self, prices: Dict[str, float], **kwargs) -> Signal:
        """Generate signal based on MACD."""
        symbol = kwargs.get("symbol", "AAPL")
        history = kwargs.get("history", [])
        
        if len(history) < self.config.slow_period + self.config.signal_period:
            return Signal.HOLD
        
        # Calculate EMAs
        fast_ema = self._calculate_ema(history, self.config.fast_period)
        slow_ema = self._calculate_ema(history, self.config.slow_period)
        
        # MACD line
        macd_line = fast_ema - slow_ema
        
        # Signal line (EMA of MACD)
        macd_history = [self._calculate_ema(history[:i], self.config.fast_period) - 
                       self._calculate_ema(history[:i], self.config.slow_period) 
                       for i in range(self.config.slow_period, len(history))]
        
        if not macd_history:
            return Signal.HOLD
        
        signal_line = self._calculate_ema(macd_history, self.config.signal_period)
        
        # Generate signals
        if macd_line > signal_line:
            return Signal.BUY
        elif macd_line < signal_line:
            return Signal.SELL
        else:
            return Signal.HOLD
    
    def _calculate_ema(self, data: List[float], period: int) -> float:
        """Calculate EMA."""
        if len(data) == 0:
            return 0.0
        if len(data) < period:
            return sum(data) / len(data) if data else 0.0
        
        multiplier = 2 / (period + 1)
        ema = sum(data[:period]) / period
        
        for price in data[period:]:
            ema = price * multiplier + ema * (1 - multiplier)
        
        return ema


class BollingerBandsStrategy(BaseStrategy):
    """Bollinger Bands mean reversion strategy."""
    
    def __init__(self, config: StrategyConfig = None):
        super().__init__("BollingerBands")
        self.config = config or StrategyConfig()
    
    def generate_signal(self, prices: Dict[str, float], **kwargs) -> Signal:
        """Generate signal based on Bollinger Bands."""
        symbol = kwargs.get("symbol", "AAPL")
        price = prices.get(symbol, 0)
        history = kwargs.get("history", [])
        
        if len(history) < self.config.bb_period:
            return Signal.HOLD
        
        # Calculate moving average and std dev
        recent = history[-self.config.bb_period:]
        sma = sum(recent) / len(recent)
        
        variance = sum((x - sma) ** 2 for x in recent) / len(recent)
        std_dev = variance ** 0.5
        
        upper_band = sma + (std_dev * self.config.bb_std_dev)
        lower_band = sma - (std_dev * self.config.bb_std_dev)
        
        # Generate signals
        if price < lower_band:
            return Signal.BUY
        elif price > upper_band:
            return Signal.SELL
        else:
            return Signal.HOLD


class VolumeWeightedStrategy(BaseStrategy):
    """Volume-weighted price action strategy."""
    
    def __init__(self, config: StrategyConfig = None):
        super().__init__("VolumeWeighted")
        self.config = config or StrategyConfig()
    
    def generate_signal(self, prices: Dict[str, float], **kwargs) -> Signal:
        """Generate signal based on volume profile."""
        symbol = kwargs.get("symbol", "AAPL")
        price = prices.get(symbol, 0)
        volume_data = kwargs.get("volume", [])
        history = kwargs.get("history", [])
        
        if len(history) < self.config.volume_period or len(volume_data) < self.config.volume_period:
            return Signal.HOLD
        
        # Calculate volume-weighted average price
        recent_prices = history[-self.config.volume_period:]
        recent_volumes = volume_data[-self.config.volume_period:]
        
        vwap = sum(p * v for p, v in zip(recent_prices, recent_volumes)) / sum(recent_volumes)
        
        # Volume trend
        avg_volume = sum(recent_volumes) / len(recent_volumes)
        current_volume = recent_volumes[-1]
        
        # Generate signals
        if price > vwap and current_volume > avg_volume:
            return Signal.BUY
        elif price < vwap and current_volume > avg_volume:
            return Signal.SELL
        else:
            return Signal.HOLD


class EnsembleStrategy(BaseStrategy):
    """Ensemble strategy combining multiple signals."""
    
    def __init__(self, config: StrategyConfig = None):
        super().__init__("Ensemble")
        self.config = config or StrategyConfig()
        self.strategies = [
            RSIStrategy(config),
            MACDStrategy(config),
            BollingerBandsStrategy(config),
        ]
    
    def generate_signal(self, prices: Dict[str, float], **kwargs) -> Signal:
        """Generate signal from ensemble of strategies."""
        signals = []
        
        for strategy in self.strategies:
            signal = strategy.generate_signal(prices, **kwargs)
            signals.append(signal)
        
        # Consensus voting
        buy_votes = sum(1 for s in signals if s == Signal.BUY)
        sell_votes = sum(1 for s in signals if s == Signal.SELL)
        
        if buy_votes > sell_votes and buy_votes >= 2:
            return Signal.BUY
        elif sell_votes > buy_votes and sell_votes >= 2:
            return Signal.SELL
        else:
            return Signal.HOLD


class AdaptiveStrategy(BaseStrategy):
    """Adaptive strategy that adjusts based on market conditions."""
    
    def __init__(self, config: StrategyConfig = None):
        super().__init__("Adaptive")
        self.config = config or StrategyConfig()
        self.volatility = 0.0
    
    def generate_signal(self, prices: Dict[str, float], **kwargs) -> Signal:
        """Generate signal based on market volatility."""
        symbol = kwargs.get("symbol", "AAPL")
        price = prices.get(symbol, 0)
        history = kwargs.get("history", [])
        
        if len(history) < 20:
            return Signal.HOLD
        
        # Calculate volatility
        recent_history = history[-20:]
        returns = [(recent_history[i] - recent_history[i-1]) / recent_history[i-1] 
                  for i in range(1, len(recent_history)) if recent_history[i-1] != 0]
        
        if returns:
            self.volatility = (sum(r ** 2 for r in returns) / len(returns)) ** 0.5
        else:
            self.volatility = 0.0
        
        # Adjust strategy based on volatility
        if self.volatility > 0.05:  # High volatility - mean reversion
            return BollingerBandsStrategy(self.config).generate_signal(prices, **kwargs)
        else:  # Low volatility - trend following
            return MACDStrategy(self.config).generate_signal(prices, **kwargs)
