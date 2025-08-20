"""
Logging configuration for Rumble Bot
"""
import sys
from pathlib import Path
from loguru import logger
from .config import config


def setup_logger():
    """Setup logger with file and console output"""
    
    # Remove default logger
    logger.remove()
    
    # Ensure logs directory exists
    Path(config.LOGS_DIR).mkdir(exist_ok=True)
    
    # Console logging
    logger.add(
        sys.stdout,
        level=config.LOG_LEVEL,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        colorize=True
    )
    
    # File logging
    logger.add(
        config.LOG_FILE,
        level=config.LOG_LEVEL,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        rotation="10 MB",
        retention="7 days",
        compression="zip"
    )
    
    return logger


# Initialize logger
log = setup_logger()
