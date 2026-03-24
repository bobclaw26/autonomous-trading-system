"""Centralized logging configuration."""

import logging
import logging.handlers
import os
from src.config import get_config


def setup_logger(name: str = "trading_system") -> logging.Logger:
    """
    Set up a logger with file and console handlers.
    
    Args:
        name: Logger name
    
    Returns:
        Configured logger instance
    """
    config = get_config()
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, config.logging.level))
    
    # Create logs directory if it doesn't exist
    os.makedirs(os.path.dirname(config.logging.file), exist_ok=True)
    
    # Create formatter
    formatter = logging.Formatter(config.logging.format)
    
    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        config.logging.file,
        maxBytes=config.logging.max_bytes,
        backupCount=config.logging.backup_count
    )
    file_handler.setLevel(getattr(logging, config.logging.level))
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, config.logging.level))
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger


# Global logger instance
logger = setup_logger()


def get_logger(name: str) -> logging.Logger:
    """Get a logger for a specific module."""
    return logging.getLogger(name)


class LoggerMixin:
    """Mixin to provide logging capability to classes."""
    
    @property
    def logger(self) -> logging.Logger:
        """Get logger for this class."""
        return get_logger(self.__class__.__module__)
