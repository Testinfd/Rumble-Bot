"""
Simple script to start the Telegram bot for testing
"""
import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.config import config
from src.logger import log
from src.telegram_bot import RumbleBot


def start_bot_for_testing():
    """Start the bot for testing purposes"""
    print("🤖 STARTING TELEGRAM BOT FOR TESTING")
    print("=" * 50)
    
    try:
        # Validate config
        config.validate()
        print("✅ Configuration validated")
        
        # Create and start bot
        print("🚀 Creating bot instance...")
        bot = RumbleBot()
        
        print("✅ Bot created successfully!")
        print("\n📱 Bot is now running and ready to receive messages!")
        print("=" * 50)
        print("🎯 You can now test the bot by:")
        print("   1. Sending /start to @roomblebot")
        print("   2. Sending /status to check bot status")
        print("   3. Sending a text message")
        print("   4. Uploading a small video file")
        print("\n⚠️ Note: Video uploads will trigger the full Rumble upload process!")
        print("   Make sure you want to actually upload to Rumble before sending videos.")
        print("\n🛑 Press Ctrl+C to stop the bot")
        print("=" * 50)
        
        # Start the bot
        bot.start()
        
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
        print("👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error starting bot: {e}")
        return False
    
    return True


if __name__ == "__main__":
    try:
        start_bot_for_testing()
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
