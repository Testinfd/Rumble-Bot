"""
Final working test - targets the exact checkboxes found in debug
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


def final_working_test():
    """Final test targeting the exact checkboxes we found"""
    print("🎯 FINAL WORKING TEST - Exact Checkbox Targeting")
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
    print("🎯 Target checkboxes:")
    print("   - id='crights' (rights agreement)")
    print("   - id='cterms' (terms agreement)")
    
    response = input("\nProceed with final working test? (y/N): ").strip().lower()
    if response not in ['y', 'yes']:
        print("❌ Cancelled")
        return False
    
    try:
        uploader = RumbleUploader()
        
        # Quick setup to terms page
        print("\n🚀 Quick setup...")
        
        if not uploader.login():
            print("❌ Login failed")
            return False
        
        uploader.driver.get("https://rumble.com/upload.php")
        time.sleep(3)
        
        # Upload file
        file_input = uploader.driver.find_element("xpath", "//input[@name='Filedata']")
        file_input.send_keys(str(video_file.absolute()))
        time.sleep(8)
        
        # Quick form fill
        title = f"Final Working Test - {random.randint(1000, 9999)}"
        uploader.driver.find_element("xpath", "//input[@name='title']").send_keys(title)
        uploader.driver.find_element("xpath", "//input[@name='primary-category']").send_keys("News")
        
        # Channel and visibility
        channel_radio = uploader.driver.find_element("xpath", "//input[@name='channelId']")
        uploader.driver.execute_script("arguments[0].click();", channel_radio)
        
        public_radio = uploader.driver.find_element("xpath", "//input[@id='visibility_public']")
        uploader.driver.execute_script("arguments[0].click();", public_radio)
        
        print("✅ Setup complete")
        
        # First submit
        print("\n🚀 First submit...")
        submit_button = uploader.driver.find_element("xpath", "//input[@id='submitForm']")
        uploader.driver.execute_script("arguments[0].click();", submit_button)
        time.sleep(5)
        
        # NOW TARGET THE EXACT CHECKBOXES
        print("\n🎯 TARGETING EXACT CHECKBOXES...")
        
        # Method 1: Target by exact ID
        print("📋 Method 1: Target by exact ID...")
        
        success_count = 0
        
        # Checkbox 1: crights
        try:
            print("   Targeting id='crights'...")
            crights_checkbox = uploader.driver.find_element("xpath", "//input[@id='crights']")
            
            # Force check with JavaScript
            uploader.driver.execute_script("""
                var checkbox = arguments[0];
                checkbox.checked = true;
                checkbox.dispatchEvent(new Event('change', { bubbles: true }));
                checkbox.dispatchEvent(new Event('click', { bubbles: true }));
            """, crights_checkbox)
            
            # Verify
            is_checked = uploader.driver.execute_script("return arguments[0].checked;", crights_checkbox)
            if is_checked:
                print("   ✅ crights checkbox CHECKED")
                success_count += 1
            else:
                print("   ❌ crights checkbox NOT checked")
                
        except Exception as e:
            print(f"   ❌ crights error: {e}")
        
        # Checkbox 2: cterms
        try:
            print("   Targeting id='cterms'...")
            cterms_checkbox = uploader.driver.find_element("xpath", "//input[@id='cterms']")
            
            # Force check with JavaScript
            uploader.driver.execute_script("""
                var checkbox = arguments[0];
                checkbox.checked = true;
                checkbox.dispatchEvent(new Event('change', { bubbles: true }));
                checkbox.dispatchEvent(new Event('click', { bubbles: true }));
            """, cterms_checkbox)
            
            # Verify
            is_checked = uploader.driver.execute_script("return arguments[0].checked;", cterms_checkbox)
            if is_checked:
                print("   ✅ cterms checkbox CHECKED")
                success_count += 1
            else:
                print("   ❌ cterms checkbox NOT checked")
                
        except Exception as e:
            print(f"   ❌ cterms error: {e}")
        
        print(f"\n📊 Checkbox Results: {success_count}/2 checkboxes checked")
        
        # Method 2: Alternative approach if needed
        if success_count < 2:
            print("\n📋 Method 2: Alternative approach...")
            
            # Try setting hidden form values directly
            try:
                uploader.driver.execute_script("""
                    // Set hidden form values
                    var rightsInput = document.getElementById('rights');
                    var termsInput = document.getElementById('terms');
                    
                    if (rightsInput) {
                        rightsInput.value = '1';
                        console.log('Set rights value to 1');
                    }
                    
                    if (termsInput) {
                        termsInput.value = '1';
                        console.log('Set terms value to 1');
                    }
                    
                    // Also try to check the checkboxes again
                    var crightsBox = document.getElementById('crights');
                    var ctermsBox = document.getElementById('cterms');
                    
                    if (crightsBox) {
                        crightsBox.checked = true;
                        crightsBox.setAttribute('checked', 'checked');
                    }
                    
                    if (ctermsBox) {
                        ctermsBox.checked = true;
                        ctermsBox.setAttribute('checked', 'checked');
                    }
                """)
                print("   ✅ Alternative method applied")
                
            except Exception as e:
                print(f"   ❌ Alternative method error: {e}")
        
        # Wait before final submit
        time.sleep(3)
        
        # FINAL SUBMIT
        print("\n🏁 FINAL SUBMIT...")
        
        try:
            # Find submit button
            submit_button2 = uploader.driver.find_element("xpath", "//input[@id='submitForm2']")
            
            # Scroll to button
            uploader.driver.execute_script("arguments[0].scrollIntoView();", submit_button2)
            time.sleep(1)
            
            # Click with JavaScript
            uploader.driver.execute_script("arguments[0].click();", submit_button2)
            print("✅ FINAL SUBMIT CLICKED")
            
            # Wait for result
            time.sleep(8)
            
            # Check final result
            final_url = uploader.driver.current_url
            final_title = uploader.driver.title
            
            print(f"\n🎉 FINAL RESULTS:")
            print(f"   URL: {final_url}")
            print(f"   Title: {final_title}")
            
            # Check for success indicators
            success_keywords = ['success', 'complete', 'uploaded', 'processing', 'video', 'view']
            
            if any(keyword in final_url.lower() or keyword in final_title.lower() for keyword in success_keywords):
                print("🎉 UPLOAD SUCCESS DETECTED!")
                
                # Move video to processed
                timestamp = int(time.time())
                new_path = processed_dir / f"final_success_{timestamp}_{video_file.name}"
                video_file.rename(new_path)
                print(f"📁 Video moved to: {new_path}")
                
                return True
            else:
                print("⚠️ Upload status unclear")
                return False
                
        except Exception as e:
            print(f"❌ Final submit error: {e}")
            return False
        
    except Exception as e:
        print(f"❌ Test error: {e}")
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
    print("🧪 Final Working Test - Exact Checkbox Targeting")
    print("=" * 60)
    
    try:
        config.validate()
    except Exception as e:
        print(f"❌ Config error: {e}")
        return False
    
    print("🎯 This test targets the EXACT checkboxes found:")
    print("   ✅ id='crights' - Rights agreement checkbox")
    print("   ✅ id='cterms' - Terms agreement checkbox")
    print("   ✅ JavaScript force-checking with events")
    print("   ✅ Hidden form value fallback")
    print("   ✅ Final submit with id='submitForm2'")
    
    return final_working_test()


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
