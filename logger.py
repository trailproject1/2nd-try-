"""
Logging configuration for the bot.

Sets up structured logging with file and console handlers.
"""

import logging
import logging.handlers
from pathlib import Path
from typing import Optional

from config import Config


def setup_logging(
    log_level: Optional[str] = None,
    log_dir: Optional[str] = None,
) -> None:
    """
    Configure logging for the application.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_dir: Directory for log files
    """
    config = Config()
    level = log_level or config.LOG_LEVEL
    log_dir = log_dir or config.LOG_DIR

    # Create log directory
    Path(log_dir).mkdir(parents=True, exist_ok=True)

    # Get logging level
    numeric_level = getattr(logging, level.upper(), logging.INFO)

    # Create logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)

    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Create formatter
    formatter = logging.Formatter(
        fmt=(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        ),
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # File Handler (rotating)
    file_handler = logging.handlers.RotatingFileHandler(
        filename=Path(log_dir) / "bot.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setLevel(numeric_level)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    # Error File Handler
    error_handler = logging.handlers.RotatingFileHandler(
        filename=Path(log_dir) / "bot_errors.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding="utf-8",
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    root_logger.addHandler(error_handler)

    # Suppress overly verbose libraries
    logging.getLogger("telegram").setLevel(logging.WARNING)
    logging.getLogger("apscheduler").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    root_logger.info(f"Logging configured - Level: {level}, Dir: {log_dir}")
