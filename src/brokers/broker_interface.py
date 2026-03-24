"""Broker API integration interface for live trading (Phase 3)."""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class Account:
    """Broker account information."""
    account_id: str
    balance: float
    buying_power: float
    positions: Dict[str, float]
    cash: float


@dataclass
class Order:
    """Order placed with broker."""
    order_id: str
    symbol: str
    side: str  # BUY or SELL
    quantity: float
    order_type: str  # MARKET, LIMIT, STOP
    price: Optional[float]
    status: str  # PENDING, FILLED, CANCELLED
    filled_quantity: float


class BrokerInterface(ABC):
    """Abstract interface for broker APIs."""
    
    @abstractmethod
    def connect(self, credentials: Dict) -> bool:
        """Connect to broker with credentials."""
        pass
    
    @abstractmethod
    def get_account_info(self) -> Account:
        """Get current account information."""
        pass
    
    @abstractmethod
    def place_order(self, symbol: str, side: str, quantity: float, 
                   order_type: str = "MARKET", price: Optional[float] = None) -> Order:
        """Place an order."""
        pass
    
    @abstractmethod
    def cancel_order(self, order_id: str) -> bool:
        """Cancel an existing order."""
        pass
    
    @abstractmethod
    def get_positions(self) -> Dict[str, float]:
        """Get current positions."""
        pass
    
    @abstractmethod
    def get_price(self, symbol: str) -> float:
        """Get current price for symbol."""
        pass
    
    @abstractmethod
    def get_price_history(self, symbol: str, days: int = 100) -> List[Dict]:
        """Get price history."""
        pass


class AlpacaBroker(BrokerInterface):
    """Alpaca broker API integration."""
    
    def __init__(self):
        self.connected = False
        self.api = None  # Would import alpaca_trade_api here
        self.base_url = "https://api.alpaca.markets"
    
    def connect(self, credentials: Dict) -> bool:
        """Connect to Alpaca."""
        # Implementation would use alpaca_trade_api library
        self.connected = True
        return self.connected
    
    def get_account_info(self) -> Account:
        """Get Alpaca account info."""
        # Would call self.api.get_account()
        return Account(
            account_id="demo",
            balance=100_000,
            buying_power=100_000,
            positions={},
            cash=100_000
        )
    
    def place_order(self, symbol: str, side: str, quantity: float,
                   order_type: str = "MARKET", price: Optional[float] = None) -> Order:
        """Place order with Alpaca."""
        # Would call self.api.submit_order()
        return Order(
            order_id="1",
            symbol=symbol,
            side=side,
            quantity=quantity,
            order_type=order_type,
            price=price,
            status="PENDING",
            filled_quantity=0
        )
    
    def cancel_order(self, order_id: str) -> bool:
        """Cancel Alpaca order."""
        # Would call self.api.cancel_order()
        return True
    
    def get_positions(self) -> Dict[str, float]:
        """Get Alpaca positions."""
        # Would call self.api.list_positions()
        return {}
    
    def get_price(self, symbol: str) -> float:
        """Get Alpaca price."""
        # Would call price API
        return 100.0
    
    def get_price_history(self, symbol: str, days: int = 100) -> List[Dict]:
        """Get Alpaca price history."""
        # Would call historical data API
        return []


class InteractiveBrokersBroker(BrokerInterface):
    """Interactive Brokers API integration."""
    
    def __init__(self):
        self.connected = False
        self.client = None  # Would import ibapi here
    
    def connect(self, credentials: Dict) -> bool:
        """Connect to Interactive Brokers."""
        self.connected = True
        return self.connected
    
    def get_account_info(self) -> Account:
        """Get IB account info."""
        return Account(
            account_id="demo",
            balance=100_000,
            buying_power=100_000,
            positions={},
            cash=100_000
        )
    
    def place_order(self, symbol: str, side: str, quantity: float,
                   order_type: str = "MARKET", price: Optional[float] = None) -> Order:
        """Place order with IB."""
        return Order(
            order_id="1",
            symbol=symbol,
            side=side,
            quantity=quantity,
            order_type=order_type,
            price=price,
            status="PENDING",
            filled_quantity=0
        )
    
    def cancel_order(self, order_id: str) -> bool:
        """Cancel IB order."""
        return True
    
    def get_positions(self) -> Dict[str, float]:
        """Get IB positions."""
        return {}
    
    def get_price(self, symbol: str) -> float:
        """Get IB price."""
        return 100.0
    
    def get_price_history(self, symbol: str, days: int = 100) -> List[Dict]:
        """Get IB price history."""
        return []


class BrokerFactory:
    """Factory for creating broker instances."""
    
    BROKERS = {
        "alpaca": AlpacaBroker,
        "interactive_brokers": InteractiveBrokersBroker,
    }
    
    @staticmethod
    def create_broker(broker_name: str) -> BrokerInterface:
        """Create broker instance."""
        broker_class = BrokerFactory.BROKERS.get(broker_name.lower())
        
        if not broker_class:
            raise ValueError(f"Unknown broker: {broker_name}")
        
        return broker_class()
