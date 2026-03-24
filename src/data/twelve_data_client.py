"""Twelve Data API client for market data."""

import os
from typing import Dict, List, Optional
from datetime import datetime
from .models import OHLCV, Quote


class TwelveDataClient:
    """Client for Twelve Data API integration."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("TWELVE_DATA_API_KEY", "demo")
        self.base_url = "https://api.twelvedata.com"
        self.rate_limit = 800  # requests per minute for free tier
        self.cached_data = {}
    
    def get_quote(self, symbol: str) -> Optional[Quote]:
        """Get real-time price quote."""
        try:
            # In production, would call: 
            # response = requests.get(f"{self.base_url}/quote", 
            #                        params={"symbol": symbol, "apikey": self.api_key})
            
            # Mock data for demo
            return Quote(
                timestamp=datetime.utcnow(),
                symbol=symbol,
                bid=99.50,
                ask=99.60,
                last=99.55,
                volume=1000000
            )
        except Exception as e:
            print(f"Error fetching quote for {symbol}: {e}")
            return None
    
    def get_timeseries(self, symbol: str, interval: str = "1day", 
                      outputsize: int = 100) -> List[OHLCV]:
        """Get historical OHLCV data."""
        try:
            # In production, would call:
            # response = requests.get(f"{self.base_url}/time_series",
            #                        params={"symbol": symbol, "interval": interval,
            #                               "outputsize": outputsize, "apikey": self.api_key})
            
            # Mock data for demo
            data = []
            price = 100.0
            for i in range(outputsize):
                price += (i % 3 - 1) * 0.5
                data.append(OHLCV(
                    timestamp=datetime.utcnow(),
                    open=price,
                    high=price * 1.02,
                    low=price * 0.98,
                    close=price,
                    volume=1000000,
                    symbol=symbol
                ))
            return data
        except Exception as e:
            print(f"Error fetching timeseries for {symbol}: {e}")
            return []
    
    def get_price(self, symbol: str) -> float:
        """Get current price for symbol."""
        quote = self.get_quote(symbol)
        return quote.last if quote else 0.0
    
    def is_market_open(self) -> bool:
        """Check if market is currently open."""
        # Simplified - in production would check actual market hours
        now = datetime.now()
        return now.weekday() < 5  # Monday-Friday
