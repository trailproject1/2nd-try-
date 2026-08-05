"""
Configuration management for the Telegram Chat Cleaner Bot.

Loads configuration from environment variables with sensible defaults.
"""

import os
from pathlib import Path
from dotenv import load_dotenv


class Config:
    """Configuration class for the bot."""

    # Load environment variables from .env file
    ENV_FILE = Path(__file__).parent / ".env"
    if ENV_FILE.exists():
        load_dotenv(ENV_FILE)

    # Bot Configuration
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    if not BOT_TOKEN:
        raise ValueError(
            "BOT_TOKEN environment variable is not set. "
            "Please set it in .env file or as environment variable."
        )

    # Database Configuration
    DATABASE_PATH: str = os.getenv("DATABASE_PATH", "data/bot.db")
    
    # Logging Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_DIR: str = os.getenv("LOG_DIR", "logs")
    
    # Default Bot Settings
    DEFAULT_DELETE_TIME_MINUTES: int = int(
        os.getenv("DEFAULT_DELETE_TIME_MINUTES", "10")
    )
    
    # Feature Flags
    ENABLE_AUTO_DELETE_BY_DEFAULT: bool = os.getenv(
        "ENABLE_AUTO_DELETE_BY_DEFAULT", "true"
    ).lower() in ("true", "1", "yes")
    
    # Timeout and Retry Configuration
    REQUEST_TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT", "30"))
    MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "3"))
    
    # Admin Notification Settings
    NOTIFY_ADMIN_ON_ERROR: bool = os.getenv(
        "NOTIFY_ADMIN_ON_ERROR", "false"
    ).lower() in ("true", "1", "yes")
    ADMIN_ID: int | None = (
        int(os.getenv("ADMIN_ID")) if os.getenv("ADMIN_ID") else None
    )

    @classmethod
    def validate(cls) -> bool:
        """Validate critical configuration."""
        if not cls.BOT_TOKEN:
            raise ValueError("BOT_TOKEN is required")
        
        # Ensure database directory exists
        db_dir = Path(cls.DATABASE_PATH).parent
        db_dir.mkdir(parents=True, exist_ok=True)
        
        # Ensure log directory exists
        log_dir = Path(cls.LOG_DIR)
        log_dir.mkdir(parents=True, exist_ok=True)
        
        return True

    def __repr__(self) -> str:
        """Return configuration summary."""
        return (
            f"Config("
            f"BOT_TOKEN='***', "
            f"DATABASE_PATH='{self.DATABASE_PATH}', "
            f"LOG_LEVEL='{self.LOG_LEVEL}', "
            f"DEFAULT_DELETE_TIME_MINUTES={self.DEFAULT_DELETE_TIME_MINUTES}, "
            f"ENABLE_AUTO_DELETE_BY_DEFAULT={self.ENABLE_AUTO_DELETE_BY_DEFAULT}"
            f")"
        )


# Validate configuration on import
Config.validate()
