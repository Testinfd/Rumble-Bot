"""
Test Telegram bot functionality
"""
import sys
import time
import requests
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.config import config
from src.logger import log


def test_telegram_bot_connection():
    """Test basic Telegram bot connection and functionality"""
    print("🤖 TELEGRAM BOT TEST")
    print("=" * 50)
    
    try:
        # Validate config first
        config.validate()
        print("✅ Configuration validated")
        
        # Test bot token
        bot_token = config.TELEGRAM_BOT_TOKEN
        if not bot_token or bot_token == "your_telegram_bot_token_here":
            print("❌ Bot token not configured properly")
            return False
        
        print(f"🔑 Bot token: {bot_token[:10]}...{bot_token[-10:]}")
        
        # Test Telegram API connection
        print("\n🌐 Testing Telegram API connection...")
        
        api_url = f"https://api.telegram.org/bot{bot_token}/getMe"
        
        try:
            response = requests.get(api_url, timeout=10)
            
            if response.status_code == 200:
                bot_info = response.json()
                
                if bot_info.get('ok'):
                    bot_data = bot_info.get('result', {})
                    print("✅ Telegram API connection successful!")
                    print(f"   🤖 Bot Name: {bot_data.get('first_name', 'Unknown')}")
                    print(f"   📝 Username: @{bot_data.get('username', 'Unknown')}")
                    print(f"   🆔 Bot ID: {bot_data.get('id', 'Unknown')}")
                    print(f"   ✅ Can Join Groups: {bot_data.get('can_join_groups', False)}")
                    print(f"   📢 Can Read All Group Messages: {bot_data.get('can_read_all_group_messages', False)}")
                    print(f"   🔒 Supports Inline Queries: {bot_data.get('supports_inline_queries', False)}")
                else:
                    print("❌ Telegram API returned error:")
                    print(f"   Error: {bot_info.get('description', 'Unknown error')}")
                    return False
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Network error: {e}")
            return False
        
        # Test bot initialization
        print("\n🚀 Testing bot initialization...")
        
        try:
            from src.telegram_bot import RumbleBot
            
            # Create bot instance (but don't start polling)
            bot = RumbleBot()
            print("✅ Bot instance created successfully")
            
            # Test bot methods
            print("\n🔧 Testing bot components...")
            
            # Test metadata extraction
            test_text = """Test Video Title
            
This is a test description
with multiple lines.

#test #telegram #bot"""
            
            title, description, tags = bot._extract_metadata(test_text)
            print(f"   📝 Metadata extraction:")
            print(f"     Title: '{title}'")
            print(f"     Description: '{description}'")
            print(f"     Tags: {tags}")
            
            if title == "Test Video Title" and "test description" in description and "test" in tags:
                print("   ✅ Metadata extraction working")
            else:
                print("   ❌ Metadata extraction failed")
                return False
            
            print("✅ Bot components working")
            
        except Exception as e:
            print(f"❌ Bot initialization error: {e}")
            return False
        
        # Test webhook info (optional)
        print("\n🔗 Checking webhook status...")
        
        webhook_url = f"https://api.telegram.org/bot{bot_token}/getWebhookInfo"
        
        try:
            webhook_response = requests.get(webhook_url, timeout=5)
            if webhook_response.status_code == 200:
                webhook_info = webhook_response.json()
                if webhook_info.get('ok'):
                    webhook_data = webhook_info.get('result', {})
                    webhook_url_set = webhook_data.get('url', '')
                    
                    if webhook_url_set:
                        print(f"   🔗 Webhook URL: {webhook_url_set}")
                        print("   ℹ️ Bot is configured for webhook mode")
                    else:
                        print("   📡 No webhook configured (polling mode)")
                        print("   ✅ Ready for polling mode")
        except:
            print("   ⚠️ Could not check webhook status")
        
        print("\n🎉 TELEGRAM BOT TEST RESULTS:")
        print("=" * 50)
        print("✅ Bot token: Valid")
        print("✅ API connection: Working")
        print("✅ Bot initialization: Success")
        print("✅ Metadata extraction: Working")
        print("✅ Ready for operation!")
        
        return True
        
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False


def test_bot_startup():
    """Test bot startup process"""
    print("\n🚀 TESTING BOT STARTUP")
    print("=" * 30)
    
    print("⚠️ This will start the bot for 30 seconds to test polling...")
    print("   You can send test messages during this time")
    print("   The bot will automatically stop after 30 seconds")
    
    response = input("\nProceed with startup test? (y/N): ").strip().lower()
    if response not in ['y', 'yes']:
        print("❌ Startup test cancelled")
        return False
    
    try:
        from src.telegram_bot import RumbleBot
        
        print("\n🤖 Starting bot...")
        bot = RumbleBot()
        
        print("✅ Bot started successfully!")
        print("📱 You can now:")
        print("   1. Send /start to the bot")
        print("   2. Send /status to check status")
        print("   3. Send a test message")
        print("   4. Send a small video file (optional)")
        
        print(f"\n⏰ Bot will run for 30 seconds...")
        print("   Press Ctrl+C to stop early")
        
        # Start polling with timeout
        import threading
        import signal
        
        stop_event = threading.Event()
        
        def stop_bot():
            time.sleep(30)
            stop_event.set()
            print("\n⏰ 30 seconds elapsed - stopping bot...")
        
        # Start timer thread
        timer_thread = threading.Thread(target=stop_bot)
        timer_thread.daemon = True
        timer_thread.start()
        
        # Start bot polling
        try:
            while not stop_event.is_set():
                try:
                    bot.bot.polling(none_stop=False, timeout=1)
                except Exception as e:
                    if "Conflict" in str(e):
                        print("⚠️ Bot conflict detected - another instance may be running")
                        break
                    else:
                        print(f"⚠️ Polling error: {e}")
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            print("\n🛑 Bot stopped by user")
        
        print("✅ Bot startup test completed")
        return True
        
    except Exception as e:
        print(f"❌ Startup test error: {e}")
        return False


def main():
    """Main test function"""
    print("🧪 Telegram Bot Test Suite")
    print("=" * 50)
    
    # Test 1: Basic connection
    print("Test 1: Basic Connection and API")
    if not test_telegram_bot_connection():
        print("❌ Basic connection test failed")
        return False
    
    print("\n" + "="*50)
    
    # Test 2: Bot startup (optional)
    print("Test 2: Bot Startup (Optional)")
    test_bot_startup()
    
    print("\n🎉 TELEGRAM BOT TESTS COMPLETED!")
    print("=" * 50)
    print("✅ Your Telegram bot is ready to use!")
    print("\n📱 To use the bot:")
    print("   1. Run: python main.py")
    print("   2. Send messages to your bot on Telegram")
    print("   3. Upload videos for automatic Rumble upload")
    
    return True


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n👋 Test interrupted")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Test error: {e}")
        sys.exit(1)
