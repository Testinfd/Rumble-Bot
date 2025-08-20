"""
Test actual video upload to Rumble using the provided video file
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


def test_actual_upload():
    """Test uploading the actual video file"""
    print("🚀 Testing Actual Video Upload to Rumble")
    print("=" * 60)
    
    # Find the video file
    video_file = Path("downloads") / "1.1 Welcome .mp4"
    
    if not video_file.exists():
        print(f"❌ Video file not found: {video_file}")
        return False
    
    print(f"📹 Found video file: {video_file}")
    print(f"📊 File size: {video_file.stat().st_size / 1024 / 1024:.2f} MB")
    
    # Ask for confirmation
    print(f"\n⚠️  WARNING: This will upload '{video_file.name}' to your Rumble account!")
    print(f"   Account: {config.RUMBLE_EMAIL}")
    print(f"   Channel: {config.RUMBLE_CHANNEL}")
    
    response = input("\nDo you want to proceed with the upload? (y/N): ")
    if response.lower() != 'y':
        print("❌ Upload cancelled by user")
        return False
    
    try:
        # Generate test metadata
        metadata_gen = MetadataGenerator()
        title = f"[TEST] Welcome Video Upload Test"
        description = f"[TEST UPLOAD] This is a test upload from the Rumble Bot. Video: {video_file.name}"
        tags = ["test", "bot", "automated", "welcome", "upload"]
        
        print(f"\n📝 Upload Details:")
        print(f"   Title: {title}")
        print(f"   Description: {description}")
        print(f"   Tags: {', '.join(tags)}")
        print(f"   Channel: {config.RUMBLE_CHANNEL}")
        
        # Create uploader and test
        print(f"\n🔧 Initializing uploader...")
        uploader = RumbleUploader()
        
        # Test login
        print(f"🔐 Logging in...")
        if not uploader.login():
            print("❌ Login failed")
            return False
        
        print("✅ Login successful!")
        
        # Navigate to upload page
        print(f"📄 Navigating to upload page...")
        uploader.driver.get("https://rumble.com/upload.php")
        time.sleep(3)
        
        print(f"   Current URL: {uploader.driver.current_url}")
        
        # Upload the video
        print(f"\n📤 Starting video upload...")
        result = uploader.upload_video(
            video_path=str(video_file),
            title=title,
            description=description,
            tags=tags,
            channel=config.RUMBLE_CHANNEL
        )
        
        # Show results
        print(f"\n📊 Upload Results:")
        print("=" * 40)
        
        if result.get('success'):
            print("✅ Upload Successful!")
            print(f"   Duration: {result.get('duration', 0)} seconds")
            print(f"   URL: {result.get('url', 'Processing...')}")
            
            # Move the video file to a processed folder
            processed_dir = Path("processed")
            processed_dir.mkdir(exist_ok=True)
            
            new_path = processed_dir / video_file.name
            video_file.rename(new_path)
            print(f"   Video moved to: {new_path}")
            
            return True
        else:
            print("❌ Upload Failed!")
            print(f"   Error: {result.get('error', 'Unknown error')}")
            print(f"   Duration: {result.get('duration', 0)} seconds")
            return False
            
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False
    
    finally:
        # Keep browser open for inspection
        print(f"\n⏸️  Browser will stay open for 30 seconds for inspection...")
        try:
            if uploader and uploader.driver:
                time.sleep(30)
                uploader.close()
        except:
            pass


def test_upload_page_only():
    """Just test navigating to upload page and inspecting elements"""
    print("🔍 Testing Upload Page Access")
    print("=" * 40)
    
    try:
        uploader = RumbleUploader()
        
        # Login
        if not uploader.login():
            print("❌ Login failed")
            return False
        
        print("✅ Login successful!")
        
        # Navigate to upload page
        print(f"📄 Navigating to: https://rumble.com/upload.php")
        uploader.driver.get("https://rumble.com/upload.php")
        time.sleep(5)
        
        print(f"   Current URL: {uploader.driver.current_url}")
        print(f"   Page Title: {uploader.driver.title}")
        
        # Check for upload elements
        print(f"\n🔍 Checking upload page elements...")
        
        # File input
        file_inputs = uploader.driver.find_elements("xpath", "//input[@type='file']")
        print(f"   File inputs found: {len(file_inputs)}")
        
        # Title field
        title_inputs = uploader.driver.find_elements("xpath", "//input[@name='title'] | //input[contains(@placeholder, 'title')]")
        print(f"   Title fields found: {len(title_inputs)}")
        
        # Description field
        desc_inputs = uploader.driver.find_elements("xpath", "//textarea[@name='description'] | //textarea[contains(@placeholder, 'description')]")
        print(f"   Description fields found: {len(desc_inputs)}")
        
        # Channel selector
        channel_selects = uploader.driver.find_elements("xpath", "//select[contains(@name, 'channel')] | //select[contains(@id, 'channel')]")
        print(f"   Channel selectors found: {len(channel_selects)}")
        
        if channel_selects:
            from selenium.webdriver.support.ui import Select
            select = Select(channel_selects[0])
            print(f"   Channel options:")
            for option in select.options:
                print(f"     - {option.text}")
        
        # Wait for inspection
        print(f"\n⏸️  Browser open for manual inspection (60 seconds)...")
        time.sleep(60)
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    finally:
        try:
            if uploader and uploader.driver:
                uploader.close()
        except:
            pass


def main():
    """Main function"""
    print("🧪 Rumble Upload Test Options")
    print("=" * 40)
    print("1. Test upload page access only")
    print("2. Test actual video upload")
    
    choice = input("\nSelect option (1 or 2): ").strip()
    
    if choice == "1":
        return test_upload_page_only()
    elif choice == "2":
        return test_actual_upload()
    else:
        print("❌ Invalid choice")
        return False


if __name__ == "__main__":
    try:
        config.validate()
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        sys.exit(1)
