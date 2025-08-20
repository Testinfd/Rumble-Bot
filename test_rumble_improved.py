"""
Improved Rumble upload test with cookie reuse and better confirmations
"""
import sys
import os
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.config import config
from src.logger import log
from src.rumble_uploader import RumbleUploader
from src.metadata_generator import MetadataGenerator


def get_user_confirmation(message: str, default: str = "n") -> bool:
    """Get user confirmation with clear prompt"""
    while True:
        response = input(f"{message} (y/N): ").strip().lower()
        if not response:
            response = default
        
        if response in ['y', 'yes']:
            return True
        elif response in ['n', 'no']:
            return False
        else:
            print("Please enter 'y' for yes or 'n' for no")


def show_config():
    """Display current configuration"""
    print("🔧 Current Configuration:")
    print("=" * 40)
    print(f"   Rumble Email: {config.RUMBLE_EMAIL}")
    print(f"   Rumble Channel: {config.RUMBLE_CHANNEL or 'Default'}")
    print(f"   Headless Mode: {config.HEADLESS_MODE}")
    print(f"   Log Level: {config.LOG_LEVEL}")
    print()


def test_login_only():
    """Test login functionality with cookie reuse"""
    print("🔐 Testing Login with Cookie Reuse")
    print("=" * 50)
    
    try:
        uploader = RumbleUploader()
        
        print("🍪 Checking for existing cookies...")
        if os.path.exists(uploader.cookies_file):
            print(f"   Found cookie file: {uploader.cookies_file}")
        else:
            print("   No existing cookies found")
        
        # Test login
        print("\n🔑 Attempting login...")
        if uploader.login():
            print("✅ Login successful!")
            print(f"   Current URL: {uploader.driver.current_url}")
            
            # Test navigation to upload page
            print("\n📄 Testing upload page access...")
            uploader.driver.get(uploader.upload_url)
            time.sleep(3)
            
            print(f"   Upload page URL: {uploader.driver.current_url}")
            
            # Check if we're still logged in
            if "login" not in uploader.driver.current_url.lower():
                print("✅ Successfully accessed upload page!")
                return uploader
            else:
                print("❌ Redirected to login page")
                return None
        else:
            print("❌ Login failed!")
            return None
            
    except Exception as e:
        print(f"❌ Login test error: {e}")
        return None


def inspect_upload_page(uploader):
    """Inspect the upload page elements"""
    print("\n🔍 Inspecting Upload Page Elements")
    print("=" * 50)
    
    try:
        # Make sure we're on upload page
        uploader.driver.get(uploader.upload_url)
        time.sleep(3)
        
        print(f"📄 Current URL: {uploader.driver.current_url}")
        print(f"📝 Page Title: {uploader.driver.title}")
        
        # Check for key elements
        elements_found = {}
        
        # File input
        file_inputs = uploader.driver.find_elements("xpath", "//input[@type='file']")
        elements_found['file_input'] = len(file_inputs)
        print(f"   📁 File inputs: {len(file_inputs)}")
        
        # Title field
        title_inputs = uploader.driver.find_elements("xpath", "//input[@name='title'] | //input[contains(@placeholder, 'title')]")
        elements_found['title_field'] = len(title_inputs)
        print(f"   📝 Title fields: {len(title_inputs)}")
        
        # Description field
        desc_inputs = uploader.driver.find_elements("xpath", "//textarea[@name='description'] | //textarea[contains(@placeholder, 'description')]")
        elements_found['description_field'] = len(desc_inputs)
        print(f"   📄 Description fields: {len(desc_inputs)}")
        
        # Channel selector
        channel_selects = uploader.driver.find_elements("xpath", "//select[contains(@name, 'channel')] | //select[contains(@id, 'channel')]")
        elements_found['channel_selector'] = len(channel_selects)
        print(f"   📺 Channel selectors: {len(channel_selects)}")
        
        if channel_selects:
            try:
                from selenium.webdriver.support.ui import Select
                select = Select(channel_selects[0])
                print(f"   📺 Available channels:")
                for i, option in enumerate(select.options):
                    marker = " ⭐" if option.text == config.RUMBLE_CHANNEL else ""
                    print(f"      {i+1}. {option.text}{marker}")
            except Exception as e:
                print(f"   ⚠️ Could not read channel options: {e}")
        
        # Submit button
        submit_buttons = uploader.driver.find_elements("xpath", "//input[@type='submit'] | //button[@type='submit'] | //button[contains(text(), 'Upload')]")
        elements_found['submit_button'] = len(submit_buttons)
        print(f"   🚀 Submit buttons: {len(submit_buttons)}")
        
        # Summary
        print(f"\n📊 Element Summary:")
        ready_for_upload = all([
            elements_found['file_input'] > 0,
            elements_found['title_field'] > 0,
            elements_found['description_field'] > 0,
            elements_found['submit_button'] > 0
        ])
        
        if ready_for_upload:
            print("✅ Upload page appears ready for video upload!")
        else:
            print("⚠️ Some required elements missing:")
            if elements_found['file_input'] == 0:
                print("   - No file input found")
            if elements_found['title_field'] == 0:
                print("   - No title field found")
            if elements_found['description_field'] == 0:
                print("   - No description field found")
            if elements_found['submit_button'] == 0:
                print("   - No submit button found")
        
        return ready_for_upload
        
    except Exception as e:
        print(f"❌ Inspection error: {e}")
        return False


def test_actual_upload(uploader):
    """Test actual video upload"""
    print("\n🚀 Testing Actual Video Upload")
    print("=" * 50)
    
    # Find video file
    video_file = Path("downloads") / "1.1 Welcome .mp4"
    
    if not video_file.exists():
        print(f"❌ Video file not found: {video_file}")
        return False
    
    print(f"📹 Video file: {video_file.name}")
    print(f"📊 File size: {video_file.stat().st_size / 1024 / 1024:.2f} MB")
    
    # Generate metadata
    metadata_gen = MetadataGenerator()
    title = f"[TEST] Welcome Video Upload - {int(time.time())}"
    description = f"[TEST UPLOAD] Automated test upload from Rumble Bot.\n\nOriginal file: {video_file.name}\nUpload time: {time.strftime('%Y-%m-%d %H:%M:%S')}"
    tags = ["test", "bot", "automated", "welcome", "upload"]
    
    print(f"\n📝 Upload Metadata:")
    print(f"   Title: {title}")
    print(f"   Description: {description[:100]}...")
    print(f"   Tags: {', '.join(tags)}")
    print(f"   Channel: {config.RUMBLE_CHANNEL or 'Default'}")
    
    # Final confirmation
    print(f"\n⚠️  FINAL CONFIRMATION")
    print(f"   This will upload '{video_file.name}' to your Rumble account!")
    print(f"   Account: {config.RUMBLE_EMAIL}")
    print(f"   Channel: {config.RUMBLE_CHANNEL or 'Default'}")
    
    if not get_user_confirmation("Proceed with actual upload?"):
        print("❌ Upload cancelled by user")
        return False
    
    try:
        print(f"\n📤 Starting upload...")
        start_time = time.time()
        
        result = uploader.upload_video(
            video_path=str(video_file),
            title=title,
            description=description,
            tags=tags,
            channel=config.RUMBLE_CHANNEL
        )
        
        duration = time.time() - start_time
        
        print(f"\n📊 Upload Results:")
        print("=" * 40)
        
        if result.get('success'):
            print("✅ Upload Successful!")
            print(f"   Duration: {duration:.1f} seconds")
            print(f"   URL: {result.get('url', 'Processing...')}")
            
            # Move video to processed folder
            processed_dir = Path("processed")
            processed_dir.mkdir(exist_ok=True)
            
            new_path = processed_dir / f"uploaded_{int(time.time())}_{video_file.name}"
            video_file.rename(new_path)
            print(f"   Video moved to: {new_path}")
            
            return True
        else:
            print("❌ Upload Failed!")
            print(f"   Error: {result.get('error', 'Unknown error')}")
            print(f"   Duration: {duration:.1f} seconds")
            return False
            
    except Exception as e:
        print(f"❌ Upload error: {e}")
        return False


def main():
    """Main test function"""
    print("🧪 Improved Rumble Upload Test")
    print("=" * 60)
    
    # Show configuration
    show_config()
    
    # Validate config
    try:
        config.validate()
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False
    
    # Test login
    uploader = test_login_only()
    if not uploader:
        print("\n❌ Cannot proceed without successful login")
        return False
    
    try:
        # Inspect upload page
        if not inspect_upload_page(uploader):
            print("\n⚠️ Upload page inspection failed")
            if not get_user_confirmation("Continue anyway?"):
                return False
        
        # Ask if user wants to proceed with actual upload
        print(f"\n🤔 What would you like to do next?")
        print("   1. Just test login and page inspection (completed)")
        print("   2. Proceed with actual video upload")
        
        choice = input("Enter choice (1 or 2): ").strip()
        
        if choice == "2":
            return test_actual_upload(uploader)
        else:
            print("✅ Test completed successfully!")
            return True
        
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False
    
    finally:
        # Keep browser open for inspection
        if uploader and uploader.driver:
            if get_user_confirmation("Keep browser open for manual inspection?"):
                print("🔍 Browser staying open for manual inspection...")
                print("   Close this terminal or press Ctrl+C when done")
                try:
                    while True:
                        time.sleep(10)
                except KeyboardInterrupt:
                    print("\n👋 Closing browser...")
            
            uploader.close()


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n👋 Test interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)
