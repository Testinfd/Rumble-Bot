"""
Main entry point for Rumble Bot
"""
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.config import config
from src.logger import log
from src.telegram_bot import RumbleBot
from src.health_check import health_checker


def main():
    """Main function to start the bot"""
    try:
        # Validate configuration
        config.validate()
        log.info("Configuration validated successfully")

        # Start health check server
        health_checker.start_server()
        health_checker.update_status("initializing")

        # Create bot instance
        bot = RumbleBot()

        # Update status and start the bot
        health_checker.update_status("running")
        log.info("Starting Rumble Bot...")
        bot.start()
        
    except ValueError as e:
        log.error(f"Configuration error: {e}")
        log.error("Please check your .env file and ensure all required variables are set")
        sys.exit(1)
    except KeyboardInterrupt:
        log.info("Bot stopped by user")
        sys.exit(0)
    except Exception as e:
        log.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
