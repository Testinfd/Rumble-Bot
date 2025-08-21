"""
Test to improve success detection and see what happens after final submit
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


def test_success_detection():
    """Test with improved success detection"""
    print("🎯 SUCCESS DETECTION TEST - Improved Final Step")
    print("=" * 60)
    
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
    print("🎯 Focus: Improved success detection after final submit")
    
    # Simple metadata
    title = f"Success Detection Test - {random.randint(1000, 9999)}"
    
    response = input("\nProceed with success detection test? (y/N): ").strip().lower()
    if response not in ['y', 'yes']:
        print("❌ Cancelled")
        return False
    
    try:
        uploader = RumbleUploader()
        
        # Quick setup (we know this works)
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
        
        uploader.driver.find_element("xpath", "//input[@name='title']").send_keys(title)
        uploader.driver.find_element("xpath", "//input[@name='primary-category']").send_keys("News")
        
        # Channel selection
        label = uploader.driver.find_element("xpath", "//label[contains(text(), 'The GRYD')]")
        for_attr = label.get_attribute('for')
        radio = uploader.driver.find_element("xpath", f"//input[@id='{for_attr}']")
        uploader.driver.execute_script("arguments[0].checked = true; arguments[0].dispatchEvent(new Event('change'));", radio)
        
        # Visibility
        visibility_radio = uploader.driver.find_element("xpath", "//input[@id='visibility_public']")
        uploader.driver.execute_script("arguments[0].checked = true; arguments[0].dispatchEvent(new Event('change'));", visibility_radio)
        
        print("✅ Setup complete")
        
        # First submit
        print("\n🚀 First submit...")
        submit_button = uploader.driver.find_element("xpath", "//input[@id='submitForm']")
        uploader.driver.execute_script("arguments[0].click();", submit_button)
        time.sleep(5)
        
        # Terms/conditions
        print("\n📜 Terms/conditions...")
        crights = uploader.driver.find_element("xpath", "//input[@id='crights']")
        cterms = uploader.driver.find_element("xpath", "//input[@id='cterms']")
        
        uploader.driver.execute_script("arguments[0].checked = true; arguments[0].dispatchEvent(new Event('change'));", crights)
        uploader.driver.execute_script("arguments[0].checked = true; arguments[0].dispatchEvent(new Event('change'));", cterms)
        
        print("✅ Both checkboxes checked")
        
        # IMPROVED FINAL SUBMIT AND SUCCESS DETECTION
        print("\n🏁 Final submit with improved detection...")
        
        # Get current state
        before_url = uploader.driver.current_url
        before_title = uploader.driver.title
        print(f"Before submit - URL: {before_url}")
        print(f"Before submit - Title: {before_title}")
        
        # Click final submit
        final_button = uploader.driver.find_element("xpath", "//input[@id='submitForm2']")
        uploader.driver.execute_script("arguments[0].click();", final_button)
        print("✅ Final submit clicked")
        
        # IMPROVED SUCCESS DETECTION WITH MULTIPLE CHECKS
        print("\n🎯 IMPROVED SUCCESS DETECTION...")
        
        # Wait and check multiple times
        for attempt in range(1, 11):  # Check 10 times over 30 seconds
            time.sleep(3)
            
            current_url = uploader.driver.current_url
            current_title = uploader.driver.title
            
            print(f"Attempt {attempt}:")
            print(f"  URL: {current_url}")
            print(f"  Title: {current_title}")
            
            # Check for success indicators
            success_indicators = []
            
            # URL-based indicators
            if "/v" in current_url and "rumble.com" in current_url:
                success_indicators.append("Video URL detected")
            
            if "success" in current_url.lower():
                success_indicators.append("Success in URL")
            
            if current_url != before_url:
                success_indicators.append("URL changed from upload page")
            
            # Title-based indicators
            if "success" in current_title.lower():
                success_indicators.append("Success in title")
            
            if "complete" in current_title.lower():
                success_indicators.append("Complete in title")
            
            if "uploaded" in current_title.lower():
                success_indicators.append("Uploaded in title")
            
            if current_title != before_title:
                success_indicators.append("Title changed")
            
            # Page content indicators
            try:
                page_source = uploader.driver.page_source.lower()
                
                if "upload successful" in page_source:
                    success_indicators.append("Upload successful in page")
                
                if "video uploaded" in page_source:
                    success_indicators.append("Video uploaded in page")
                
                if "processing" in page_source:
                    success_indicators.append("Processing detected")
                
                # Look for video embed or player
                if "video" in page_source and "player" in page_source:
                    success_indicators.append("Video player detected")
                
            except:
                pass
            
            # Check for error indicators
            error_indicators = []
            
            if "error" in current_url.lower() or "error" in current_title.lower():
                error_indicators.append("Error detected")
            
            if "upload.php" in current_url and attempt > 5:
                error_indicators.append("Still on upload page after 15 seconds")
            
            # Report findings
            if success_indicators:
                print(f"  ✅ Success indicators: {', '.join(success_indicators)}")
            
            if error_indicators:
                print(f"  ❌ Error indicators: {', '.join(error_indicators)}")
            
            if not success_indicators and not error_indicators:
                print(f"  ⏳ No clear indicators yet...")
            
            # Determine if we should stop checking
            if len(success_indicators) >= 2:  # Multiple success indicators
                print(f"\n🎉 SUCCESS DETECTED! ({len(success_indicators)} indicators)")
                return True
            
            if error_indicators:
                print(f"\n❌ ERROR DETECTED! ({', '.join(error_indicators)})")
                break
            
            # Special case: if URL changed significantly, that's usually success
            if current_url != before_url and "upload.php" not in current_url:
                print(f"\n🎉 SUCCESS! URL changed to non-upload page")
                return True
        
        # Final assessment
        print(f"\n📊 FINAL ASSESSMENT:")
        final_url = uploader.driver.current_url
        final_title = uploader.driver.title
        
        print(f"Final URL: {final_url}")
        print(f"Final Title: {final_title}")
        
        if final_url != before_url:
            print("🎉 URL CHANGED - Likely successful!")
            return True
        else:
            print("⚠️ URL unchanged - Upload may have failed or is still processing")
            return False
        
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False
    
    finally:
        # Keep browser open for manual verification
        if uploader and uploader.driver:
            response = input("\nKeep browser open for manual verification? (y/N): ").strip().lower()
            if response in ['y', 'yes']:
                print("🔍 Browser open for manual verification...")
                print("   Check the current page and your Rumble account")
                print("   Look for the uploaded video")
                print("   Close terminal when done")
                try:
                    while True:
                        time.sleep(10)
                except KeyboardInterrupt:
                    print("\n👋 Closing...")
            
            uploader.close()


def main():
    """Main function"""
    print("🧪 Success Detection Test")
    print("=" * 50)
    
    try:
        config.validate()
    except Exception as e:
        print(f"❌ Config error: {e}")
        return False
    
    print("🎯 This test focuses on:")
    print("   📊 Multiple success detection methods")
    print("   ⏱️ Time-based monitoring after final submit")
    print("   🔍 URL and title change detection")
    print("   📄 Page content analysis")
    print("   ❌ Error detection")
    
    return test_success_detection()


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
