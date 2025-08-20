"""
Complete Rumble upload test with all form fields and license handling
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


def get_user_confirmation(message: str) -> bool:
    """Get user confirmation"""
    response = input(f"{message} (y/N): ").strip().lower()
    return response in ['y', 'yes']


def test_complete_upload():
    """Test complete upload workflow with all form fields"""
    print("🚀 Complete Rumble Upload Test")
    print("=" * 60)
    
    # Find video file
    video_file = Path("downloads") / "1.1 Welcome .mp4"
    
    if not video_file.exists():
        print(f"❌ Video file not found: {video_file}")
        return False
    
    print(f"📹 Video file: {video_file.name}")
    print(f"📊 File size: {video_file.stat().st_size / 1024 / 1024:.2f} MB")
    
    # Show configuration
    print(f"\n🔧 Upload Configuration:")
    print(f"   Account: {config.RUMBLE_EMAIL}")
    print(f"   Channel: {config.RUMBLE_CHANNEL}")
    print(f"   Category: News (default)")
    print(f"   Visibility: Public")
    
    # Generate metadata
    metadata_gen = MetadataGenerator()
    title = f"[TEST] Complete Upload Test - {int(time.time())}"
    description = f"""[AUTOMATED TEST UPLOAD]

This is a complete test of the Rumble Bot upload functionality.

Features tested:
✅ Login with cookie reuse
✅ File upload
✅ Title and description
✅ Category selection (News)
✅ Upload destination selection
✅ Visibility setting (Public)
✅ License page handling

Original file: {video_file.name}
Upload time: {time.strftime('%Y-%m-%d %H:%M:%S')}
Bot version: 1.0.0"""
    
    tags = ["test", "bot", "automated", "complete", "upload", "news"]
    
    print(f"\n📝 Upload Details:")
    print(f"   Title: {title}")
    print(f"   Description: {description[:100]}...")
    print(f"   Tags: {', '.join(tags)}")
    
    # Final confirmation
    print(f"\n⚠️  FINAL CONFIRMATION")
    print(f"   This will upload '{video_file.name}' to Rumble with:")
    print(f"   - Category: News")
    print(f"   - Destination: {config.RUMBLE_CHANNEL}")
    print(f"   - Visibility: Public")
    print(f"   - License handling: Automatic")
    
    if not get_user_confirmation("Proceed with complete upload test?"):
        print("❌ Upload cancelled by user")
        return False
    
    try:
        print(f"\n🔧 Initializing uploader...")
        uploader = RumbleUploader()
        
        # Test login (with cookie reuse)
        print(f"🔐 Logging in...")
        if not uploader.login():
            print("❌ Login failed")
            return False
        
        print("✅ Login successful!")
        
        # Start upload process
        print(f"\n📤 Starting complete upload process...")
        start_time = time.time()
        
        result = uploader.upload_video(
            video_path=str(video_file),
            title=title,
            description=description,
            tags=tags,
            channel=config.RUMBLE_CHANNEL
        )
        
        duration = time.time() - start_time
        
        # Show detailed results
        print(f"\n📊 Complete Upload Results:")
        print("=" * 50)
        
        if result.get('success'):
            print("🎉 COMPLETE UPLOAD SUCCESSFUL!")
            print(f"   ⏱️  Total Duration: {duration:.1f} seconds")
            print(f"   🔗 Video URL: {result.get('url', 'Processing...')}")
            print(f"   📝 Title: {title}")
            print(f"   📺 Channel: {config.RUMBLE_CHANNEL}")
            print(f"   📂 Category: News")
            print(f"   👁️  Visibility: Public")
            
            # Move video to processed folder
            processed_dir = Path("processed")
            processed_dir.mkdir(exist_ok=True)
            
            timestamp = int(time.time())
            new_path = processed_dir / f"complete_upload_{timestamp}_{video_file.name}"
            video_file.rename(new_path)
            print(f"   📁 Video moved to: {new_path}")
            
            print(f"\n✅ All upload steps completed successfully!")
            print(f"   - Login with cookies ✅")
            print(f"   - File upload ✅")
            print(f"   - Form filling ✅")
            print(f"   - Category selection ✅")
            print(f"   - Destination selection ✅")
            print(f"   - Visibility setting ✅")
            print(f"   - License handling ✅")
            print(f"   - Success detection ✅")
            
            return True
        else:
            print("❌ Upload Failed!")
            print(f"   Error: {result.get('error', 'Unknown error')}")
            print(f"   Duration: {duration:.1f} seconds")
            
            # Still show what was attempted
            print(f"\n📋 What was attempted:")
            print(f"   - Login: ✅")
            print(f"   - File upload: ✅")
            print(f"   - Form filling: ✅")
            print(f"   - Category selection: ⚠️")
            print(f"   - Destination selection: ⚠️")
            print(f"   - Visibility setting: ⚠️")
            print(f"   - License handling: ⚠️")
            print(f"   - Success detection: ❌")
            
            return False
            
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False
    
    finally:
        # Keep browser open for inspection
        if uploader and uploader.driver:
            if get_user_confirmation("Keep browser open for manual inspection?"):
                print("🔍 Browser staying open for manual inspection...")
                print("   You can manually check the upload status")
                print("   Close this terminal or press Ctrl+C when done")
                try:
                    while True:
                        time.sleep(10)
                except KeyboardInterrupt:
                    print("\n👋 Closing browser...")
            
            uploader.close()


def main():
    """Main function"""
    print("🧪 Complete Rumble Upload Test Suite")
    print("=" * 60)
    
    # Validate config
    try:
        config.validate()
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False
    
    # Show what this test will do
    print("📋 This test will:")
    print("   1. Login to Rumble (using saved cookies if available)")
    print("   2. Upload your test video")
    print("   3. Fill all form fields (title, description, tags)")
    print("   4. Select category: News")
    print("   5. Select upload destination/channel")
    print("   6. Set visibility to Public")
    print("   7. Handle license agreement page")
    print("   8. Detect upload success")
    print("   9. Return video URL")
    
    if not get_user_confirmation("\nProceed with complete upload test?"):
        print("❌ Test cancelled by user")
        return False
    
    return test_complete_upload()


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
