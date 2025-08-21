"""
Debug script to see what happens after upload button click
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


def debug_upload_flow():
    """Debug the upload flow to see what pages we encounter"""
    print("🔍 DEBUG UPLOAD FLOW")
    print("=" * 40)
    
    # Find video file
    processed_dir = Path("processed")
    video_file = None
    
    if processed_dir.exists():
        for file in processed_dir.glob("*.mp4"):
            video_file = file
            break
    
    if not video_file:
        print("❌ No video file found")
        return False
    
    print(f"📹 Video: {video_file.name}")
    
    response = input("\nProceed with debug flow? (y/N): ").strip().lower()
    if response not in ['y', 'yes']:
        print("❌ Cancelled")
        return False
    
    try:
        uploader = RumbleUploader()
        
        # Quick setup
        print("\n🚀 Quick setup...")
        if not uploader.login():
            print("❌ Login failed")
            return False
        
        uploader.driver.get("https://rumble.com/upload.php")
        time.sleep(3)
        
        # Upload and fill forms (streamlined)
        file_input = uploader.driver.find_element("xpath", "//input[@name='Filedata']")
        file_input.send_keys(str(video_file.absolute()))
        time.sleep(8)
        
        title = f"Debug Flow Test - {random.randint(1000, 9999)}"
        uploader.driver.find_element("xpath", "//input[@name='title']").send_keys(title)
        uploader.driver.find_element("xpath", "//input[@name='primary-category']").send_keys("News")
        
        # Channel selection
        channel_radio = uploader.driver.find_element("xpath", "//input[@name='channelId']")
        uploader.driver.execute_script("arguments[0].click();", channel_radio)
        
        # Visibility
        try:
            public_radio = uploader.driver.find_element("xpath", "//input[@id='visibility_public']")
            uploader.driver.execute_script("arguments[0].click();", public_radio)
        except:
            print("⚠️ Visibility radio not found")
        
        print("✅ Setup complete")
        
        # First submit and debug what happens
        print("\n🚀 First submit...")
        submit_button = uploader.driver.find_element("xpath", "//input[@id='submitForm']")
        
        before_url = uploader.driver.current_url
        before_title = uploader.driver.title
        print(f"Before submit - URL: {before_url}")
        print(f"Before submit - Title: {before_title}")
        
        uploader.driver.execute_script("arguments[0].click();", submit_button)
        
        # Monitor what happens for 30 seconds
        print("\n🔍 MONITORING PAGE CHANGES...")
        for i in range(10):  # 30 seconds total
            time.sleep(3)
            current_url = uploader.driver.current_url
            current_title = uploader.driver.title
            page_source_snippet = uploader.driver.page_source[:500]
            
            print(f"\nStep {i+1} (after {(i+1)*3}s):")
            print(f"  URL: {current_url}")
            print(f"  Title: {current_title}")
            
            # Check for license page indicators
            license_indicators = ['license', 'agreement', 'terms', 'conditions']
            is_license_page = any(indicator in current_url.lower() or indicator in current_title.lower() 
                                for indicator in license_indicators)
            
            if is_license_page:
                print(f"  🎯 LICENSE PAGE DETECTED!")
                
                # Look for checkboxes
                try:
                    crights = uploader.driver.find_elements("xpath", "//input[@id='crights']")
                    cterms = uploader.driver.find_elements("xpath", "//input[@id='cterms']")
                    print(f"  📋 Found crights: {len(crights)}, cterms: {len(cterms)}")
                    
                    if crights and cterms:
                        print("  ✅ Both checkboxes found - this is the license page!")
                        break
                except:
                    pass
            
            # Check for success indicators
            if "/v" in current_url and "rumble.com" in current_url:
                print(f"  🎉 VIDEO URL DETECTED: {current_url}")
                break
            
            if current_url != before_url and "upload.php" not in current_url:
                print(f"  📍 URL CHANGED from upload page")
            
            # Check page content for clues
            if "success" in page_source_snippet.lower():
                print(f"  ✅ 'Success' found in page content")
            
            if "processing" in page_source_snippet.lower():
                print(f"  ⚙️ 'Processing' found in page content")
        
        print(f"\n📊 FINAL STATE:")
        final_url = uploader.driver.current_url
        final_title = uploader.driver.title
        print(f"Final URL: {final_url}")
        print(f"Final Title: {final_title}")
        
        return True
        
    except Exception as e:
        print(f"❌ Debug error: {e}")
        return False
    
    finally:
        # Keep browser open for manual inspection
        if uploader and uploader.driver:
            response = input("\nKeep browser open for manual inspection? (y/N): ").strip().lower()
            if response in ['y', 'yes']:
                print("🔍 Browser open for manual inspection...")
                print("   Inspect the current page state")
                print("   Close terminal when done")
                try:
                    while True:
                        time.sleep(10)
                except KeyboardInterrupt:
                    print("\n👋 Closing...")
            
            uploader.close()


if __name__ == "__main__":
    try:
        debug_upload_flow()
    except KeyboardInterrupt:
        print("\n👋 Interrupted")
    except Exception as e:
        print(f"❌ Error: {e}")
