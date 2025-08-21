"""
Main entry point for Rumble Bot
"""
import sys
import os
import signal
import atexit
import threading
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.config import config
from src.logger import log
from src.telegram_bot import RumbleBot
from src.health_check import health_checker

# Global bot instance for cleanup
bot_instance = None
shutdown_event = threading.Event()


def cleanup_resources():
    """Clean up resources on shutdown"""
    global bot_instance
    try:
        log.info("Cleaning up resources...")

        if bot_instance:
            log.info("Stopping Telegram bot...")
            bot_instance.stop()

        health_checker.update_status("stopped")
        log.info("Cleanup completed")

    except Exception as e:
        log.error(f"Error during cleanup: {e}")


def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    log.info(f"Received signal {signum}, initiating graceful shutdown...")
    shutdown_event.set()
    cleanup_resources()
    sys.exit(0)


def main():
    """Main function to start the bot"""
    global bot_instance

    try:
        # Validate configuration
        config.validate()
        log.info("Configuration validated successfully")

        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        atexit.register(cleanup_resources)

        # Start health check server
        health_checker.start_server()
        health_checker.update_status("initializing")

        # Create bot instance
        bot_instance = RumbleBot()

        # Update status and start the bot
        health_checker.update_status("running")
        log.info("Starting Rumble Bot...")
        log.info("Press Ctrl+C to stop the bot gracefully")
        bot_instance.start()

    except ValueError as e:
        log.error(f"Configuration error: {e}")
        log.error("Please check your .env file and ensure all required variables are set")
        sys.exit(1)
    except KeyboardInterrupt:
        log.info("Bot stopped by user (Ctrl+C)")
        shutdown_event.set()
    except Exception as e:
        log.error(f"Unexpected error: {e}")
        health_checker.update_status("error", str(e))
        sys.exit(1)
    finally:
        cleanup_resources()


if __name__ == "__main__":
    main()
