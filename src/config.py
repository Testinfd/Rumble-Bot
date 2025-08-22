"""
Configuration management for Rumble Bot
"""
import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Configuration class for the Rumble Bot"""
    
    # Telegram Configuration
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_CHAT_ID: Optional[str] = os.getenv("TELEGRAM_CHAT_ID")

    # Telegram API credentials for Pyrogram (for large file downloads)
    TELEGRAM_API_ID: Optional[str] = os.getenv("TELEGRAM_API_ID")
    TELEGRAM_API_HASH: Optional[str] = os.getenv("TELEGRAM_API_HASH")
    
    # Rumble Credentials
    RUMBLE_EMAIL: str = os.getenv("RUMBLE_EMAIL", "")
    RUMBLE_PASSWORD: str = os.getenv("RUMBLE_PASSWORD", "")
    RUMBLE_CHANNEL: Optional[str] = os.getenv("RUMBLE_CHANNEL")  # Channel name to upload to
    
    # Bot Settings
    MAX_FILE_SIZE_MB: int = int(os.getenv("MAX_FILE_SIZE_MB", "2048"))
    UPLOAD_TIMEOUT_SECONDS: int = int(os.getenv("UPLOAD_TIMEOUT_SECONDS", "1800"))
    RETRY_ATTEMPTS: int = int(os.getenv("RETRY_ATTEMPTS", "3"))
    RETRY_DELAY_SECONDS: int = int(os.getenv("RETRY_DELAY_SECONDS", "30"))
    
    # Selenium Configuration
    HEADLESS_MODE: bool = os.getenv("HEADLESS_MODE", "true").lower() == "true"
    SELENIUM_TIMEOUT: int = int(os.getenv("SELENIUM_TIMEOUT", "30"))
    IMPLICIT_WAIT: int = int(os.getenv("IMPLICIT_WAIT", "10"))
    
    # Logging Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "logs/rumble_bot.log")
    
    # Deployment Configuration
    PORT: int = int(os.getenv("PORT", "8080"))
    HOST: str = os.getenv("HOST", "0.0.0.0")
    WEBHOOK_URL: Optional[str] = os.getenv("WEBHOOK_URL")
    
    # Random Content Generation
    ENABLE_RANDOM_TITLES: bool = os.getenv("ENABLE_RANDOM_TITLES", "true").lower() == "true"
    ENABLE_RANDOM_DESCRIPTIONS: bool = os.getenv("ENABLE_RANDOM_DESCRIPTIONS", "true").lower() == "true"
    ENABLE_RANDOM_TAGS: bool = os.getenv("ENABLE_RANDOM_TAGS", "true").lower() == "true"

    # Telegram Bot Features
    ENABLE_PROGRESS_UPDATES: bool = os.getenv("ENABLE_PROGRESS_UPDATES", "true").lower() == "true"
    ENABLE_DEBUG_INFO: bool = os.getenv("ENABLE_DEBUG_INFO", "true").lower() == "true"
    
    # Directories
    DOWNLOADS_DIR: str = "downloads"
    TEMP_DIR: str = "temp"
    LOGS_DIR: str = "logs"
    
    @classmethod
    def validate(cls) -> bool:
        """Validate required configuration"""
        required_fields = [
            "TELEGRAM_BOT_TOKEN",
            "RUMBLE_EMAIL", 
            "RUMBLE_PASSWORD"
        ]
        
        missing_fields = []
        for field in required_fields:
            if not getattr(cls, field):
                missing_fields.append(field)
        
        if missing_fields:
            raise ValueError(f"Missing required configuration: {', '.join(missing_fields)}")
        
        return True


# Create config instance
config = Config()
