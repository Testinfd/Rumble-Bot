"""
Debug script to inspect Rumble login page
"""
import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.config import config
from src.logger import log
from src.rumble_uploader import RumbleUploader


def debug_login_page():
    """Debug the Rumble login page to see current structure"""
    print("🔍 Debugging Rumble Login Page...")
    print("=" * 50)
    
    try:
        uploader = RumbleUploader()
        uploader.driver = uploader._setup_driver()
        
        # Navigate to login page
        print(f"📍 Navigating to: {uploader.login_url}")
        uploader.driver.get(uploader.login_url)
        time.sleep(3)
        
        print(f"📄 Current URL: {uploader.driver.current_url}")
        print(f"📝 Page Title: {uploader.driver.title}")
        
        # Try to find various login elements
        print("\n🔍 Looking for login form elements...")
        
        # Check for email/username fields
        email_selectors = [
            "//input[@name='username']",
            "//input[@name='email']", 
            "//input[@type='email']",
            "//input[contains(@placeholder, 'email')]",
            "//input[contains(@placeholder, 'Email')]",
            "//input[contains(@id, 'email')]",
            "//input[contains(@id, 'username')]"
        ]
        
        for selector in email_selectors:
            try:
                elements = uploader.driver.find_elements("xpath", selector)
                if elements:
                    print(f"✅ Found email field: {selector}")
                    element = elements[0]
                    print(f"   - Tag: {element.tag_name}")
                    print(f"   - Name: {element.get_attribute('name')}")
                    print(f"   - ID: {element.get_attribute('id')}")
                    print(f"   - Placeholder: {element.get_attribute('placeholder')}")
                    break
            except:
                continue
        else:
            print("❌ No email field found")
        
        # Check for password fields
        password_selectors = [
            "//input[@name='password']",
            "//input[@type='password']",
            "//input[contains(@placeholder, 'password')]",
            "//input[contains(@placeholder, 'Password')]",
            "//input[contains(@id, 'password')]"
        ]
        
        for selector in password_selectors:
            try:
                elements = uploader.driver.find_elements("xpath", selector)
                if elements:
                    print(f"✅ Found password field: {selector}")
                    element = elements[0]
                    print(f"   - Tag: {element.tag_name}")
                    print(f"   - Name: {element.get_attribute('name')}")
                    print(f"   - ID: {element.get_attribute('id')}")
                    print(f"   - Placeholder: {element.get_attribute('placeholder')}")
                    break
            except:
                continue
        else:
            print("❌ No password field found")
        
        # Check for submit buttons
        submit_selectors = [
            "//input[@type='submit']",
            "//button[@type='submit']",
            "//button[contains(text(), 'Login')]",
            "//button[contains(text(), 'Sign in')]",
            "//button[contains(text(), 'Log in')]",
            "//input[@value='Login']",
            "//input[@value='Sign in']",
            "//input[@value='Log in']"
        ]
        
        for selector in submit_selectors:
            try:
                elements = uploader.driver.find_elements("xpath", selector)
                if elements:
                    print(f"✅ Found submit button: {selector}")
                    element = elements[0]
                    print(f"   - Tag: {element.tag_name}")
                    print(f"   - Type: {element.get_attribute('type')}")
                    print(f"   - Value: {element.get_attribute('value')}")
                    print(f"   - Text: {element.text}")
                    print(f"   - Class: {element.get_attribute('class')}")
                    break
            except:
                continue
        else:
            print("❌ No submit button found")
        
        # Get page source snippet around forms
        print("\n📄 Looking for forms on the page...")
        try:
            forms = uploader.driver.find_elements("xpath", "//form")
            print(f"Found {len(forms)} form(s)")
            
            for i, form in enumerate(forms):
                print(f"\n📋 Form {i+1}:")
                print(f"   - Action: {form.get_attribute('action')}")
                print(f"   - Method: {form.get_attribute('method')}")
                print(f"   - Class: {form.get_attribute('class')}")
                
                # Find inputs in this form
                inputs = form.find_elements("xpath", ".//input")
                print(f"   - Inputs: {len(inputs)}")
                for j, inp in enumerate(inputs):
                    print(f"     Input {j+1}: type={inp.get_attribute('type')}, name={inp.get_attribute('name')}")
        except Exception as e:
            print(f"Error inspecting forms: {e}")
        
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
    debug_login_page()
