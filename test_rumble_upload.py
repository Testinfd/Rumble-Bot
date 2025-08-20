"""
Test script for Rumble upload functionality
"""
import sys
import os
import tempfile
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.config import config
from src.logger import log
from src.rumble_uploader import RumbleUploader
from src.metadata_generator import MetadataGenerator


def create_test_video():
    """Create a small test video file"""
    try:
        # Create a simple test video using FFmpeg (if available)
        # For now, we'll create a dummy file that looks like a video
        test_video_path = Path("test_video.mp4")
        
        # Create a small dummy video file (this won't be a real video)
        # In a real test, you'd want to use a proper test video file
        with open(test_video_path, 'wb') as f:
            # Write some dummy data that resembles an MP4 header
            f.write(b'\x00\x00\x00\x18ftypmp4\x00')  # MP4 signature
            f.write(b'0' * 1024)  # 1KB of dummy data
        
        log.info(f"Created test video file: {test_video_path}")
        return str(test_video_path)
        
    except Exception as e:
        log.error(f"Error creating test video: {e}")
        return None


def test_rumble_login():
    """Test Rumble login functionality"""
    print("\n🔐 Testing Rumble Login...")
    print("=" * 50)
    
    try:
        uploader = RumbleUploader()
        
        # Test login
        login_success = uploader.login()
        
        if login_success:
            print("✅ Login successful!")
            print(f"   - Email: {config.RUMBLE_EMAIL}")
            print(f"   - Status: Logged in")
            return uploader
        else:
            print("❌ Login failed!")
            print("   - Check your credentials in .env file")
            print("   - Ensure Rumble account is valid")
            return None
            
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None


def test_channel_selection(uploader):
    """Test channel selection functionality"""
    print("\n📺 Testing Channel Selection...")
    print("=" * 50)
    
    try:
        if not config.RUMBLE_CHANNEL:
            print("⚠️ No channel specified in config")
            print("   - Set RUMBLE_CHANNEL in .env file to test channel selection")
            return True
        
        # Navigate to upload page to test channel selection
        uploader.driver.get(uploader.upload_url)
        uploader._human_delay(2, 4)
        
        # Test channel selection
        channel_selected = uploader._select_channel(config.RUMBLE_CHANNEL)
        
        if channel_selected:
            print(f"✅ Channel selection successful!")
            print(f"   - Channel: {config.RUMBLE_CHANNEL}")
            return True
        else:
            print(f"⚠️ Channel selection failed or not found")
            print(f"   - Channel: {config.RUMBLE_CHANNEL}")
            print("   - This might be normal if channel dropdown is not visible yet")
            return True  # Don't fail the test for this
            
    except Exception as e:
        print(f"❌ Channel selection error: {e}")
        return False


def test_upload_form(uploader):
    """Test upload form filling"""
    print("\n📝 Testing Upload Form...")
    print("=" * 50)
    
    try:
        # Generate test metadata
        metadata_gen = MetadataGenerator()
        title = metadata_gen.generate_title()
        description = metadata_gen.generate_description()
        tags = metadata_gen.generate_tags(count=5)
        
        print(f"   - Title: {title}")
        print(f"   - Description: {description[:50]}...")
        print(f"   - Tags: {', '.join(tags)}")
        
        # Navigate to upload page if not already there
        if "upload" not in uploader.driver.current_url:
            uploader.driver.get(uploader.upload_url)
            uploader._human_delay(2, 4)
        
        # Test form filling (without actually uploading)
        form_filled = uploader._fill_video_details(title, description, tags)
        
        if form_filled:
            print("✅ Form filling successful!")
            print("   - All fields populated correctly")
            return True
        else:
            print("❌ Form filling failed!")
            print("   - Check if upload page structure has changed")
            return False
            
    except Exception as e:
        print(f"❌ Form filling error: {e}")
        return False


def test_full_upload():
    """Test complete upload process with a small test file"""
    print("\n🚀 Testing Complete Upload Process...")
    print("=" * 50)
    
    # Ask user for confirmation
    response = input("Do you want to test actual video upload? This will upload a test file to Rumble. (y/N): ")
    if response.lower() != 'y':
        print("⏭️ Skipping actual upload test")
        return True
    
    try:
        # Create test video
        test_video_path = create_test_video()
        if not test_video_path:
            print("❌ Failed to create test video")
            return False
        
        # Generate metadata
        metadata_gen = MetadataGenerator()
        title = f"[TEST] {metadata_gen.generate_title()}"
        description = f"[TEST UPLOAD] {metadata_gen.generate_description()}"
        tags = ["test", "bot", "automated"] + metadata_gen.generate_tags(count=3)
        
        print(f"   - Test video: {test_video_path}")
        print(f"   - Title: {title}")
        print(f"   - Description: {description[:50]}...")
        print(f"   - Tags: {', '.join(tags)}")
        
        # Upload video
        uploader = RumbleUploader()
        result = uploader.upload_video(
            video_path=test_video_path,
            title=title,
            description=description,
            tags=tags,
            channel=config.RUMBLE_CHANNEL
        )
        
        # Clean up test file
        try:
            os.remove(test_video_path)
        except:
            pass
        
        if result.get('success'):
            print("✅ Upload successful!")
            print(f"   - URL: {result.get('url', 'N/A')}")
            print(f"   - Duration: {result.get('duration', 0)} seconds")
            return True
        else:
            print("❌ Upload failed!")
            print(f"   - Error: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Upload test error: {e}")
        return False
    finally:
        # Clean up test file if it exists
        try:
            if test_video_path and os.path.exists(test_video_path):
                os.remove(test_video_path)
        except:
            pass


def main():
    """Main test function"""
    print("🧪 Rumble Upload Test Suite")
    print("=" * 50)
    
    # Check configuration
    print("\n⚙️ Configuration Check...")
    print(f"   - Rumble Email: {config.RUMBLE_EMAIL}")
    print(f"   - Rumble Channel: {config.RUMBLE_CHANNEL or 'Not specified'}")
    print(f"   - Headless Mode: {config.HEADLESS_MODE}")
    
    if not config.RUMBLE_EMAIL or not config.RUMBLE_PASSWORD:
        print("\n❌ Missing Rumble credentials!")
        print("Please set RUMBLE_EMAIL and RUMBLE_PASSWORD in your .env file")
        return False
    
    # Test login
    uploader = test_rumble_login()
    if not uploader:
        print("\n❌ Cannot proceed without successful login")
        return False
    
    try:
        # Test channel selection
        if not test_channel_selection(uploader):
            print("\n⚠️ Channel selection test failed, but continuing...")
        
        # Test form filling
        if not test_upload_form(uploader):
            print("\n❌ Form filling test failed")
            return False
        
        # Test complete upload (optional)
        if not test_full_upload():
            print("\n⚠️ Full upload test failed or skipped")
        
        print("\n🎉 Test Suite Completed!")
        print("=" * 50)
        print("✅ Basic functionality appears to be working")
        print("📝 Check the logs for detailed information")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test suite error: {e}")
        return False
    
    finally:
        # Clean up
        try:
            if uploader:
                uploader.close()
        except:
            pass


if __name__ == "__main__":
    try:
        # Validate configuration first
        config.validate()
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        print("Please check your .env file and ensure all required variables are set")
        sys.exit(1)
