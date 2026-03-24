"""Machine learning models for risk prediction."""

from typing import List, Dict, Tuple
import statistics


class RiskPredictor:
    """Predicts portfolio risk using historical data."""
    
    def __init__(self):
        self.historical_volatility = []
        self.historical_drawdowns = []
        self.model_trained = False
    
    def train(self, returns: List[float]):
        """Train risk predictor on historical returns."""
        if len(returns) < 20:
            raise ValueError("Need at least 20 data points")
        
        self.historical_volatility = returns
        
        # Calculate drawdowns
        peak = 0
        drawdowns = []
        for ret in returns:
            cumulative = sum(returns[:returns.index(ret) + 1]) / 100
            if cumulative > peak:
                peak = cumulative
            
            drawdown = (peak - cumulative) / peak if peak > 0 else 0
            drawdowns.append(drawdown)
        
        self.historical_drawdowns = drawdowns
        self.model_trained = True
    
    def predict_var(self, confidence: float = 0.95) -> float:
        """Predict Value at Risk (VaR) at given confidence level."""
        if not self.model_trained:
            return 0.0
        
        sorted_returns = sorted(self.historical_volatility)
        index = int(len(sorted_returns) * (1 - confidence))
        
        return sorted_returns[index] if index < len(sorted_returns) else sorted_returns[0]
    
    def predict_max_drawdown(self) -> float:
        """Predict maximum expected drawdown."""
        if not self.historical_drawdowns:
            return 0.0
        
        return max(self.historical_drawdowns)
    
    def predict_volatility(self) -> float:
        """Predict portfolio volatility."""
        if not self.historical_volatility:
            return 0.0
        
        return statistics.stdev(self.historical_volatility) if len(self.historical_volatility) > 1 else 0.0


class SignalPredictor:
    """Predicts trading signals using historical patterns."""
    
    def __init__(self):
        self.training_data = []
        self.labels = []
        self.model_trained = False
    
    def train(self, features: List[List[float]], labels: List[str]):
        """Train signal predictor on historical data."""
        if len(features) != len(labels):
            raise ValueError("Features and labels must have same length")
        
        self.training_data = features
        self.labels = labels
        self.model_trained = True
    
    def predict(self, features: List[float]) -> str:
        """Predict signal (BUY/SELL/HOLD) from features."""
        if not self.model_trained:
            return "HOLD"
        
        # Simple nearest neighbor approach
        distances = []
        for i, training_features in enumerate(self.training_data):
            distance = sum((features[j] - training_features[j]) ** 2 
                          for j in range(len(features))) ** 0.5
            distances.append((distance, self.labels[i]))
        
        # Get 3 nearest neighbors
        nearest = sorted(distances, key=lambda x: x[0])[:3]
        
        # Voting
        votes = {}
        for _, label in nearest:
            votes[label] = votes.get(label, 0) + 1
        
        return max(votes, key=votes.get) if votes else "HOLD"
    
    def predict_confidence(self, features: List[float]) -> float:
        """Predict confidence level of signal."""
        if not self.model_trained:
            return 0.0
        
        distances = []
        for training_features in self.training_data:
            distance = sum((features[j] - training_features[j]) ** 2 
                          for j in range(len(features))) ** 0.5
            distances.append(distance)
        
        # Lower average distance = higher confidence
        avg_distance = sum(distances) / len(distances) if distances else float('inf')
        
        # Normalize to 0-1 scale
        max_possible_distance = 100
        confidence = max(0, 1 - (avg_distance / max_possible_distance))
        
        return min(1.0, confidence)
