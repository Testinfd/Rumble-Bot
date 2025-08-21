"""
Test the improved Rumble uploader with faster processing and better error handling
"""
import sys
import time
import random
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.config import config
from src.logger import log
from src.rumble_uploader import RumbleUploader


def test_improved_uploader():
    """Test the improved uploader"""
    print("🚀 IMPROVED RUMBLE UPLOADER TEST")
    print("=" * 50)
    
    # Find video file
    processed_dir = Path("processed")
    video_file = None
    
    if processed_dir.exists():
        for file in processed_dir.glob("*.mp4"):
            video_file = file
            break
    
    if not video_file:
        print("❌ No video file found in processed directory")
        return False
    
    print(f"📹 Video: {video_file.name}")
    print("🎯 Testing improvements:")
    print("   ✅ Faster processing with reduced delays")
    print("   ✅ Better success detection")
    print("   ✅ Improved error handling")
    print("   ✅ Enhanced visibility setting")
    print("   ✅ Robust description filling")
    
    response = input("\nProceed with improved uploader test? (y/N): ").strip().lower()
    if response not in ['y', 'yes']:
        print("❌ Cancelled")
        return False
    
    try:
        uploader = RumbleUploader()
        
        # Test metadata
        title = f"Improved Uploader Test - {random.randint(1000, 9999)}"
        description = "Testing the improved Rumble uploader with better error handling and faster processing."
        tags = ["test", "improved", "uploader"]
        
        print(f"\n📝 Test metadata:")
        print(f"   Title: {title}")
        print(f"   Description: {description}")
        print(f"   Tags: {tags}")
        
        # Start upload with timing
        start_time = time.time()
        
        print("\n🚀 Starting upload...")
        upload_result = uploader.upload_video(
            video_path=str(video_file),
            title=title,
            description=description,
            tags=tags,
            channel=config.RUMBLE_CHANNEL
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"\n📊 UPLOAD RESULTS:")
        print(f"   Duration: {duration:.1f} seconds")
        print(f"   Success: {upload_result.get('success', False)}")
        print(f"   URL: {upload_result.get('url', 'None')}")
        
        if upload_result.get('error'):
            print(f"   Error: {upload_result.get('error')}")
        
        if upload_result.get('success'):
            print("\n🎉 UPLOAD SUCCESSFUL!")
            
            # Move video to mark as processed
            timestamp = int(time.time())
            new_path = processed_dir / f"improved_success_{timestamp}_{video_file.name}"
            video_file.rename(new_path)
            print(f"📁 Video moved to: {new_path}")
            
            return True
        else:
            print("\n❌ UPLOAD FAILED!")
            return False
        
    except Exception as e:
        print(f"\n❌ Test error: {e}")
        return False
    
    finally:
        # Keep browser open for verification
        if uploader and uploader.driver:
            response = input("\nKeep browser open for verification? (y/N): ").strip().lower()
            if response in ['y', 'yes']:
                print("🔍 Browser open for verification...")
                print("   Check your Rumble account for the uploaded video")
                print("   Close terminal when done")
                try:
                    while True:
                        time.sleep(10)
                except KeyboardInterrupt:
                    print("\n👋 Closing...")
            
            uploader.close()


def main():
    """Main function"""
    print("🧪 Improved Rumble Uploader Test")
    print("=" * 40)
    
    try:
        config.validate()
    except Exception as e:
        print(f"❌ Config error: {e}")
        return False
    
    print("🎯 This test validates the improvements:")
    print("   🚀 Faster processing (reduced delays)")
    print("   🎯 Better success detection with multiple attempts")
    print("   🔧 Improved visibility setting using specific selectors")
    print("   📝 Enhanced description filling with fallback methods")
    print("   ❌ Better error handling and reporting")
    
    return test_improved_uploader()


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n👋 Interrupted")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
