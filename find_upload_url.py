"""
Find the correct Rumble upload URL
"""
import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.config import config
from src.logger import log
from src.rumble_uploader import RumbleUploader


def find_upload_url():
    """Find the correct upload URL on Rumble"""
    print("🔍 Finding Rumble Upload URL...")
    print("=" * 50)
    
    try:
        uploader = RumbleUploader()
        
        # Login first
        if not uploader.login():
            print("❌ Login failed")
            return
        
        print("✅ Login successful, looking for upload links...")
        
        # Stay on main page and look for upload links
        print(f"📄 Current URL: {uploader.driver.current_url}")
        
        # Look for upload links/buttons
        upload_selectors = [
            "//a[contains(@href, 'upload')]",
            "//a[contains(text(), 'Upload')]",
            "//a[contains(text(), 'upload')]",
            "//button[contains(text(), 'Upload')]",
            "//button[contains(text(), 'upload')]",
            "//div[contains(text(), 'Upload')]//parent::a",
            "//span[contains(text(), 'Upload')]//parent::a"
        ]
        
        found_links = []
        for selector in upload_selectors:
            try:
                elements = uploader.driver.find_elements("xpath", selector)
                for element in elements:
                    href = element.get_attribute('href')
                    text = element.text.strip()
                    if href and 'upload' in href.lower():
                        found_links.append((href, text, selector))
                        print(f"✅ Found upload link: {href}")
                        print(f"   - Text: '{text}'")
                        print(f"   - Selector: {selector}")
            except Exception as e:
                continue
        
        if not found_links:
            print("❌ No upload links found, checking navigation menu...")
            
            # Look in navigation/menu
            nav_selectors = [
                "//nav//a",
                "//header//a", 
                "//div[contains(@class, 'nav')]//a",
                "//div[contains(@class, 'menu')]//a"
            ]
            
            for selector in nav_selectors:
                try:
                    elements = uploader.driver.find_elements("xpath", selector)
                    for element in elements:
                        href = element.get_attribute('href')
                        text = element.text.strip()
                        if href and ('upload' in href.lower() or 'upload' in text.lower()):
                            print(f"✅ Found in navigation: {href}")
                            print(f"   - Text: '{text}'")
                except:
                    continue
        
        # Try common upload URLs
        test_urls = [
            "https://rumble.com/upload",
            "https://rumble.com/upload/",
            "https://rumble.com/studio/upload",
            "https://rumble.com/creator/upload",
            "https://rumble.com/user/upload",
            "https://studio.rumble.com/upload"
        ]
        
        print(f"\n🧪 Testing common upload URLs...")
        for url in test_urls:
            try:
                print(f"Testing: {url}")
                uploader.driver.get(url)
                time.sleep(2)
                
                current_url = uploader.driver.current_url
                title = uploader.driver.title
                
                print(f"   - Redirected to: {current_url}")
                print(f"   - Title: {title}")
                
                # Check if this looks like an upload page
                if 'upload' in current_url.lower() or 'upload' in title.lower():
                    print(f"✅ Potential upload page found: {current_url}")
                    
                    # Look for file upload
                    file_inputs = uploader.driver.find_elements("xpath", "//input[@type='file']")
                    if file_inputs:
                        print(f"   - Found {len(file_inputs)} file input(s)")
                        for i, inp in enumerate(file_inputs):
                            accept = inp.get_attribute('accept')
                            print(f"     File input {i+1}: accept={accept}")
                    
                    # Look for form fields
                    title_inputs = uploader.driver.find_elements("xpath", "//input[@name='title'] | //input[contains(@placeholder, 'title')]")
                    if title_inputs:
                        print(f"   - Found title field")
                    
                    desc_inputs = uploader.driver.find_elements("xpath", "//textarea[@name='description'] | //textarea[contains(@placeholder, 'description')]")
                    if desc_inputs:
                        print(f"   - Found description field")
                
                print()
                
            except Exception as e:
                print(f"   - Error: {e}")
                continue
        
        # Wait for manual inspection
        print(f"\n⏸️ Browser will stay open for 30 seconds for manual inspection...")
        print(f"   Current URL: {uploader.driver.current_url}")
        time.sleep(30)
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    finally:
        try:
            if uploader and uploader.driver:
                uploader.close()
        except:
            pass


if __name__ == "__main__":
    find_upload_url()
