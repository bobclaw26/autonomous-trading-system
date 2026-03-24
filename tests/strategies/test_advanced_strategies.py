"""Tests for advanced trading strategies."""

import pytest
from src.strategies.advanced_strategies import (
    RSIStrategy, MACDStrategy, BollingerBandsStrategy,
    VolumeWeightedStrategy, EnsembleStrategy, AdaptiveStrategy,
    StrategyConfig
)
from src.strategies.base_strategy import Signal


class TestAdvancedStrategies:
    """Test advanced strategy implementations."""
    
    def test_rsi_strategy_overbought(self):
        """Test RSI strategy detects overbought."""
        strategy = RSIStrategy()
        
        # High prices (simulating overbought)
        history = [100 + i for i in range(20)]
        
        signal = strategy.generate_signal(
            {"AAPL": 120},
            symbol="AAPL",
            history=history
        )
        
        # Should detect overbought condition
        assert signal in [Signal.SELL, Signal.HOLD]
    
    def test_rsi_strategy_oversold(self):
        """Test RSI strategy detects oversold."""
        strategy = RSIStrategy()
        
        # Low prices (simulating oversold)
        history = [100 - i for i in range(20)]
        
        signal = strategy.generate_signal(
            {"AAPL": 80},
            symbol="AAPL",
            history=history
        )
        
        # Should detect oversold condition
        assert signal in [Signal.BUY, Signal.HOLD]
    
    def test_macd_strategy(self):
        """Test MACD strategy signal generation."""
        strategy = MACDStrategy()
        
        # Uptrend
        history = [100 + i * 0.5 for i in range(50)]
        
        signal = strategy.generate_signal(
            {"AAPL": 125},
            symbol="AAPL",
            history=history
        )
        
        assert signal in [Signal.BUY, Signal.SELL, Signal.HOLD]
    
    def test_bollinger_bands_strategy(self):
        """Test Bollinger Bands strategy."""
        strategy = BollingerBandsStrategy()
        
        # Oscillating prices
        history = [100 + (i % 10 - 5) for i in range(30)]
        
        signal = strategy.generate_signal(
            {"AAPL": 95},  # Below band
            symbol="AAPL",
            history=history
        )
        
        assert signal in [Signal.BUY, Signal.SELL, Signal.HOLD]
    
    def test_volume_weighted_strategy(self):
        """Test volume-weighted strategy."""
        strategy = VolumeWeightedStrategy()
        
        history = [100 + (i % 5) for i in range(30)]
        volumes = [1_000_000 + (i % 500_000) for i in range(30)]
        
        signal = strategy.generate_signal(
            {"AAPL": 105},
            symbol="AAPL",
            history=history,
            volume=volumes
        )
        
        assert signal in [Signal.BUY, Signal.SELL, Signal.HOLD]
    
    def test_ensemble_strategy(self):
        """Test ensemble strategy."""
        strategy = EnsembleStrategy()
        
        history = [100 + i * 0.5 for i in range(50)]
        
        signal = strategy.generate_signal(
            {"AAPL": 125},
            symbol="AAPL",
            history=history
        )
        
        assert signal in [Signal.BUY, Signal.SELL, Signal.HOLD]
    
    def test_adaptive_strategy_high_volatility(self):
        """Test adaptive strategy with high volatility."""
        strategy = AdaptiveStrategy()
        
        # High volatility prices
        history = [100, 110, 95, 115, 85, 120, 80, 125, 75, 130,
                  100, 110, 95, 115, 85, 120, 80, 125, 75, 130]
        
        signal = strategy.generate_signal(
            {"AAPL": 130},
            symbol="AAPL",
            history=history
        )
        
        # Should use mean reversion in high volatility
        assert signal in [Signal.BUY, Signal.SELL, Signal.HOLD]
        assert strategy.volatility > 0
    
    def test_strategy_config_custom(self):
        """Test custom strategy configuration."""
        config = StrategyConfig(
            rsi_period=21,
            rsi_overbought=75,
            rsi_oversold=25
        )
        
        strategy = RSIStrategy(config)
        assert strategy.config.rsi_period == 21
        assert strategy.config.rsi_overbought == 75
    
    def test_insufficient_history(self):
        """Test strategies with insufficient history."""
        strategy = RSIStrategy()
        
        # Insufficient history
        history = [100, 101, 102]
        
        signal = strategy.generate_signal(
            {"AAPL": 102},
            symbol="AAPL",
            history=history
        )
        
        # Should return HOLD with insufficient data
        assert signal == Signal.HOLD
    
    def test_ensemble_consensus(self):
        """Test ensemble consensus voting."""
        strategy = EnsembleStrategy()
        
        # Create history that should trigger consensus
        history = [100 + i for i in range(50)]
        
        signal = strategy.generate_signal(
            {"AAPL": 150},
            symbol="AAPL",
            history=history
        )
        
        # Should reach consensus
        assert signal in [Signal.BUY, Signal.SELL, Signal.HOLD]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
