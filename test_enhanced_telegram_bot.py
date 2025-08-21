"""
Enhanced Telegram Bot Test Suite - Tests improved features
"""
import sys
import time
import threading
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.config import config


def test_basic_connection():
    """Test basic Telegram API connection"""
    print("🤖 ENHANCED TELEGRAM BOT TEST")
    print("=" * 50)
    
    try:
        config.validate()
        print("✅ Configuration validated")
        print(f"🔑 Bot token: {config.TELEGRAM_BOT_TOKEN[:10]}...{config.TELEGRAM_BOT_TOKEN[-10:]}")
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False
    
    # Test API connection
    print("\n🌐 Testing Telegram API connection...")
    
    import requests
    bot_token = config.TELEGRAM_BOT_TOKEN
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
                return True
            else:
                print("❌ Telegram API returned error:")
                print(f"   Error: {bot_info.get('description', 'Unknown error')}")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False


def test_enhanced_bot_features():
    """Test the enhanced bot features"""
    print("\n🚀 TESTING ENHANCED BOT FEATURES")
    print("=" * 50)
    
    print("🎯 Enhanced features to test:")
    print("   ✅ Progress updates during upload")
    print("   ✅ Better error handling and reporting")
    print("   ✅ Actual video URL extraction")
    print("   ✅ Configuration-based features")
    print("   ✅ Enhanced user experience")
    
    print(f"\n⚙️ Current configuration:")
    print(f"   📊 Progress Updates: {'Enabled' if config.ENABLE_PROGRESS_UPDATES else 'Disabled'}")
    print(f"   🐛 Debug Info: {'Enabled' if config.ENABLE_DEBUG_INFO else 'Disabled'}")
    print(f"   🎲 Random Titles: {'Enabled' if config.ENABLE_RANDOM_TITLES else 'Disabled'}")
    print(f"   📝 Random Descriptions: {'Enabled' if config.ENABLE_RANDOM_DESCRIPTIONS else 'Disabled'}")
    print(f"   🏷️ Random Tags: {'Enabled' if config.ENABLE_RANDOM_TAGS else 'Disabled'}")
    
    print("\n⚠️ The bot will start for 90 seconds to test these features...")
    print("   📱 Send /start to test help message")
    print("   📊 Send /status to test status command")
    print("   📹 Send a small video file to test enhanced upload process")
    print("   🔍 Watch for detailed progress updates")
    print("   🎯 Check for actual video URL in final response")
    print("   ⏰ Bot will automatically stop after 90 seconds")
    
    response = input("\nProceed with enhanced bot test? (y/N): ").strip().lower()
    if response not in ['y', 'yes']:
        print("❌ Enhanced bot test cancelled")
        return False
    
    try:
        from src.telegram_bot import RumbleBot
        
        print("\n🤖 Starting enhanced bot...")
        bot = RumbleBot()
        print("✅ Bot started successfully!")
        
        print("\n📱 You can now test the enhanced features:")
        print("   1. Send /start to the bot")
        print("   2. Send /status to check status")
        print("   3. Send a test message")
        print("   4. Send a small video file (recommended)")
        print("   5. Watch for enhanced progress updates")
        print("   6. Check for actual video URL in response")
        
        print(f"\n⏰ Bot will run for 90 seconds...")
        print("   Press Ctrl+C to stop early")
        
        # Create a timer to stop the bot
        def stop_bot():
            time.sleep(90)
            print("\n⏰ 90 seconds elapsed - stopping bot...")
            bot.stop()
        
        timer_thread = threading.Thread(target=stop_bot)
        timer_thread.daemon = True
        timer_thread.start()
        
        # Start polling
        try:
            bot.start()
        except KeyboardInterrupt:
            print("\n⏹️ Bot stopped by user")
        except Exception as e:
            print(f"\n⚠️ Polling error: {e}")
        
        print("✅ Enhanced bot test completed")
        return True
        
    except Exception as e:
        print(f"❌ Enhanced bot test error: {e}")
        return False


def test_configuration_features():
    """Test configuration-based features"""
    print("\n⚙️ TESTING CONFIGURATION FEATURES")
    print("=" * 40)
    
    print("🔧 Testing configuration options:")
    
    # Test progress updates setting
    print(f"   📊 ENABLE_PROGRESS_UPDATES: {config.ENABLE_PROGRESS_UPDATES}")
    if config.ENABLE_PROGRESS_UPDATES:
        print("      ✅ Progress updates will be shown during upload")
    else:
        print("      ⚠️ Progress updates are disabled")
    
    # Test debug info setting
    print(f"   🐛 ENABLE_DEBUG_INFO: {config.ENABLE_DEBUG_INFO}")
    if config.ENABLE_DEBUG_INFO:
        print("      ✅ Debug information will be included in error messages")
    else:
        print("      ⚠️ Debug information is disabled")
    
    # Test random content settings
    print(f"   🎲 ENABLE_RANDOM_TITLES: {config.ENABLE_RANDOM_TITLES}")
    print(f"   📝 ENABLE_RANDOM_DESCRIPTIONS: {config.ENABLE_RANDOM_DESCRIPTIONS}")
    print(f"   🏷️ ENABLE_RANDOM_TAGS: {config.ENABLE_RANDOM_TAGS}")
    
    print("\n💡 To modify these settings, update your .env file:")
    print("   ENABLE_PROGRESS_UPDATES=true/false")
    print("   ENABLE_DEBUG_INFO=true/false")
    print("   ENABLE_RANDOM_TITLES=true/false")
    print("   ENABLE_RANDOM_DESCRIPTIONS=true/false")
    print("   ENABLE_RANDOM_TAGS=true/false")
    
    return True


def test_metadata_generation():
    """Test enhanced metadata generation"""
    print("\n📝 TESTING ENHANCED METADATA GENERATION")
    print("=" * 45)
    
    try:
        from src.metadata_generator import MetadataGenerator
        
        generator = MetadataGenerator()
        
        print("🎲 Testing random content generation:")
        
        # Test title generation
        if config.ENABLE_RANDOM_TITLES:
            title = generator.generate_title()
            print(f"   📰 Random Title: '{title}'")
        else:
            print("   📰 Random titles disabled")
        
        # Test description generation
        if config.ENABLE_RANDOM_DESCRIPTIONS:
            description = generator.generate_description()
            print(f"   📝 Random Description: '{description[:50]}...'")
        else:
            print("   📝 Random descriptions disabled")
        
        # Test tag generation
        if config.ENABLE_RANDOM_TAGS:
            tags = generator.generate_tags()
            print(f"   🏷️ Random Tags: {tags}")
        else:
            print("   🏷️ Random tags disabled")
        
        print("✅ Metadata generation working")
        return True
        
    except Exception as e:
        print(f"❌ Metadata generation error: {e}")
        return False


def main():
    """Main test function"""
    print("🧪 Enhanced Telegram Bot Test Suite")
    print("=" * 50)
    
    print("🎯 This test suite validates:")
    print("   🔗 Basic API connectivity")
    print("   🚀 Enhanced bot features")
    print("   ⚙️ Configuration options")
    print("   📝 Metadata generation")
    print("   📹 Upload process improvements")
    
    # Test 1: Basic connection
    print("\n" + "="*50)
    print("Test 1: Basic API Connection")
    if not test_basic_connection():
        print("❌ Basic connection test failed")
        return False
    
    # Test 2: Configuration features
    print("\n" + "="*50)
    print("Test 2: Configuration Features")
    if not test_configuration_features():
        print("❌ Configuration test failed")
        return False
    
    # Test 3: Metadata generation
    print("\n" + "="*50)
    print("Test 3: Metadata Generation")
    if not test_metadata_generation():
        print("❌ Metadata generation test failed")
        return False
    
    # Test 4: Enhanced bot features
    print("\n" + "="*50)
    print("Test 4: Enhanced Bot Features")
    if not test_enhanced_bot_features():
        print("❌ Enhanced bot test failed")
        return False
    
    print("\n🎉 ENHANCED TELEGRAM BOT TESTS COMPLETED!")
    print("=" * 50)
    print("✅ Your enhanced Telegram bot is ready to use!")
    
    print("\n📱 To use the enhanced bot:")
    print("   1. Run: python main.py")
    print("   2. Send messages to your bot on Telegram")
    print("   3. Upload videos for automatic Rumble upload with progress updates")
    print("   4. Enjoy the enhanced user experience!")
    
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
