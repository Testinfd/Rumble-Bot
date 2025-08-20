"""
Debug script to inspect Rumble upload page
"""
import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.config import config
from src.logger import log
from src.rumble_uploader import RumbleUploader


def debug_upload_page():
    """Debug the Rumble upload page to see current structure"""
    print("🔍 Debugging Rumble Upload Page...")
    print("=" * 50)
    
    try:
        uploader = RumbleUploader()
        
        # Login first
        if not uploader.login():
            print("❌ Login failed")
            return
        
        print("✅ Login successful, navigating to upload page...")
        
        # Navigate to upload page
        uploader.driver.get(uploader.upload_url)
        time.sleep(5)
        
        print(f"📄 Current URL: {uploader.driver.current_url}")
        print(f"📝 Page Title: {uploader.driver.title}")
        
        # Look for form fields
        print("\n🔍 Looking for upload form elements...")
        
        # Check for title field
        title_selectors = [
            "//input[@name='title']",
            "//input[contains(@placeholder, 'title')]",
            "//input[contains(@placeholder, 'Title')]",
            "//input[contains(@id, 'title')]",
            "//textarea[@name='title']"
        ]
        
        for selector in title_selectors:
            try:
                elements = uploader.driver.find_elements("xpath", selector)
                if elements:
                    print(f"✅ Found title field: {selector}")
                    element = elements[0]
                    print(f"   - Tag: {element.tag_name}")
                    print(f"   - Name: {element.get_attribute('name')}")
                    print(f"   - ID: {element.get_attribute('id')}")
                    print(f"   - Enabled: {element.is_enabled()}")
                    print(f"   - Displayed: {element.is_displayed()}")
                    break
            except:
                continue
        else:
            print("❌ No title field found")
        
        # Check for description field
        description_selectors = [
            "//textarea[@name='description']",
            "//textarea[contains(@placeholder, 'description')]",
            "//textarea[contains(@placeholder, 'Description')]",
            "//textarea[contains(@id, 'description')]",
            "//input[@name='description']"
        ]
        
        for selector in description_selectors:
            try:
                elements = uploader.driver.find_elements("xpath", selector)
                if elements:
                    print(f"✅ Found description field: {selector}")
                    element = elements[0]
                    print(f"   - Tag: {element.tag_name}")
                    print(f"   - Name: {element.get_attribute('name')}")
                    print(f"   - ID: {element.get_attribute('id')}")
                    print(f"   - Enabled: {element.is_enabled()}")
                    print(f"   - Displayed: {element.is_displayed()}")
                    break
            except:
                continue
        else:
            print("❌ No description field found")
        
        # Check for file upload
        file_selectors = [
            "//input[@type='file']",
            "//input[contains(@accept, 'video')]"
        ]
        
        for selector in file_selectors:
            try:
                elements = uploader.driver.find_elements("xpath", selector)
                if elements:
                    print(f"✅ Found file upload: {selector}")
                    element = elements[0]
                    print(f"   - Accept: {element.get_attribute('accept')}")
                    print(f"   - Multiple: {element.get_attribute('multiple')}")
                    break
            except:
                continue
        else:
            print("❌ No file upload found")
        
        # Check for channel dropdown
        channel_selectors = [
            "//select[contains(@name, 'channel')]",
            "//select[contains(@id, 'channel')]",
            "//div[contains(@class, 'channel')]//select"
        ]
        
        for selector in channel_selectors:
            try:
                elements = uploader.driver.find_elements("xpath", selector)
                if elements:
                    print(f"✅ Found channel selector: {selector}")
                    element = elements[0]
                    print(f"   - Name: {element.get_attribute('name')}")
                    print(f"   - ID: {element.get_attribute('id')}")
                    
                    # List options
                    from selenium.webdriver.support.ui import Select
                    select = Select(element)
                    print(f"   - Options:")
                    for option in select.options:
                        print(f"     * {option.text} (value: {option.get_attribute('value')})")
                    break
            except Exception as e:
                print(f"Error checking channel selector: {e}")
                continue
        else:
            print("❌ No channel selector found")
        
        # Wait for manual inspection
        print(f"\n⏸️ Browser will stay open for 30 seconds for manual inspection...")
        print(f"   Current URL: {uploader.driver.current_url}")
        time.sleep(30)
        
    except Exception as e:
        print(f"❌ Debug error: {e}")
    
    finally:
        try:
            if uploader and uploader.driver:
                uploader.close()
        except:
            pass


if __name__ == "__main__":
    debug_upload_page()
