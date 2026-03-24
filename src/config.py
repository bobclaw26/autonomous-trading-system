"""Configuration management for the trading system."""

import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


@dataclass
class DataConfig:
    """Data layer configuration."""
    twelve_data_api_key: str = os.getenv("TWELVE_DATA_API_KEY", "demo")
    api_base_url: str = "https://api.twelvedata.com"
    rate_limit_requests_per_minute: int = 800
    cache_ttl_seconds: int = 300
    polling_interval_seconds: int = 60


@dataclass
class TradingConfig:
    """Trading engine configuration."""
    initial_capital: float = 100_000.0
    base_spread_bps: float = 1.0  # 1 basis point
    market_impact_bps: float = 0.5
    commission_pct: float = 0.001  # 0.1%
    max_position_pct: float = 0.05  # 5% per asset
    max_portfolio_drawdown_pct: float = 0.20  # 20%
    default_stop_loss_pct: float = 0.02  # 2%
    max_total_exposure_pct: float = 1.0  # 100% (no leverage)


@dataclass
class RiskConfig:
    """Risk management configuration."""
    max_daily_loss_pct: float = 0.05  # 5%
    sector_concentration_limit: float = 0.25  # 25%
    risk_per_trade_pct: float = 0.02  # 2%
    correlation_threshold: float = 0.7


@dataclass
class APIConfig:
    """API server configuration."""
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = os.getenv("ENV", "development") == "development"
    reload: bool = True
    cors_origins: list = None

    def __post_init__(self):
        if self.cors_origins is None:
            self.cors_origins = ["http://localhost:3000", "http://localhost:8000"]


@dataclass
class LoggingConfig:
    """Logging configuration."""
    level: str = os.getenv("LOG_LEVEL", "INFO")
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file: str = "logs/trading_system.log"
    max_bytes: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5


@dataclass
class Config:
    """Master configuration object."""
    data: DataConfig = None
    trading: TradingConfig = None
    risk: RiskConfig = None
    api: APIConfig = None
    logging: LoggingConfig = None
    env: str = os.getenv("ENV", "development")
    debug: bool = env == "development"

    def __post_init__(self):
        if self.data is None:
            self.data = DataConfig()
        if self.trading is None:
            self.trading = TradingConfig()
        if self.risk is None:
            self.risk = RiskConfig()
        if self.api is None:
            self.api = APIConfig()
        if self.logging is None:
            self.logging = LoggingConfig()


# Global configuration instance
config = Config()


def get_config() -> Config:
    """Get the global configuration instance."""
    return config


def load_config_from_file(config_file: str) -> Config:
    """Load configuration from a YAML file."""
    import yaml
    
    try:
        with open(config_file, 'r') as f:
            config_dict = yaml.safe_load(f)
        
        # Reconstruct config from dictionary
        data = DataConfig(**config_dict.get('data', {}))
        trading = TradingConfig(**config_dict.get('trading', {}))
        risk = RiskConfig(**config_dict.get('risk', {}))
        api = APIConfig(**config_dict.get('api', {}))
        logging = LoggingConfig(**config_dict.get('logging', {}))
        
        return Config(
            data=data,
            trading=trading,
            risk=risk,
            api=api,
            logging=logging
        )
    except FileNotFoundError:
        print(f"Config file {config_file} not found, using defaults")
        return config
    except Exception as e:
        print(f"Error loading config: {e}, using defaults")
        return config
