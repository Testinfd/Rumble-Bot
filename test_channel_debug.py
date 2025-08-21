"""
Debug and fix the channel selection issue for "The GRYD"
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


def debug_channel_selection():
    """Debug channel selection to find The GRYD"""
    print("📺 Channel Selection Debug - Finding 'The GRYD'")
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
    print(f"🎯 Target channel: '{config.RUMBLE_CHANNEL}'")
    
    response = input("\nProceed with channel debug? (y/N): ").strip().lower()
    if response not in ['y', 'yes']:
        print("❌ Cancelled")
        return False
    
    try:
        uploader = RumbleUploader()
        
        # Quick setup to upload page
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
        
        print("✅ File uploaded, now analyzing channel options...")
        
        # ANALYZE CHANNEL OPTIONS
        print("\n📺 CHANNEL ANALYSIS:")
        
        # Method 1: Find all channel radio buttons
        print("🔍 Method 1: All channel radio buttons...")
        channel_radios = uploader.driver.find_elements("xpath", "//input[@name='channelId']")
        print(f"Found {len(channel_radios)} channel radio buttons")
        
        for i, radio in enumerate(channel_radios):
            try:
                value = radio.get_attribute('value')
                id_attr = radio.get_attribute('id')
                is_checked = radio.is_selected()
                is_displayed = radio.is_displayed()
                is_enabled = radio.is_enabled()
                
                print(f"   Radio {i+1}:")
                print(f"     - Value: {value}")
                print(f"     - ID: {id_attr}")
                print(f"     - Checked: {is_checked}")
                print(f"     - Displayed: {is_displayed}")
                print(f"     - Enabled: {is_enabled}")
                
                # Look for associated label
                try:
                    # Try to find label by 'for' attribute
                    if id_attr:
                        label = uploader.driver.find_element("xpath", f"//label[@for='{id_attr}']")
                        label_text = label.text.strip()
                        print(f"     - Label: '{label_text}'")
                        
                        if config.RUMBLE_CHANNEL.lower() in label_text.lower():
                            print(f"     *** TARGET CHANNEL FOUND! ***")
                    
                except:
                    # Try to find nearby text
                    try:
                        parent = radio.find_element("xpath", "..")
                        parent_text = parent.text.strip()
                        if parent_text:
                            print(f"     - Parent text: '{parent_text}'")
                            
                            if config.RUMBLE_CHANNEL.lower() in parent_text.lower():
                                print(f"     *** TARGET CHANNEL FOUND IN PARENT! ***")
                    except:
                        pass
                
                print()
                
            except Exception as e:
                print(f"   Radio {i+1}: Error - {e}")
        
        # Method 2: Search for channel text in page source
        print("🔍 Method 2: Search page source for channel names...")
        page_source = uploader.driver.page_source
        
        # Look for The GRYD in various forms
        channel_variations = [
            "The GRYD",
            "TheGRYD", 
            "GRYD",
            "the gryd",
            "thegryd"
        ]
        
        for variation in channel_variations:
            count = page_source.count(variation)
            if count > 0:
                print(f"   Found '{variation}': {count} occurrences")
        
        # Method 3: Find all labels and their associated inputs
        print("\n🔍 Method 3: All labels and associated inputs...")
        labels = uploader.driver.find_elements("xpath", "//label")
        
        for i, label in enumerate(labels):
            try:
                label_text = label.text.strip()
                for_attr = label.get_attribute('for')
                
                if label_text and any(var.lower() in label_text.lower() for var in channel_variations):
                    print(f"   Label {i+1}: '{label_text}' (for='{for_attr}')")
                    
                    if for_attr:
                        try:
                            associated_input = uploader.driver.find_element("xpath", f"//input[@id='{for_attr}']")
                            input_type = associated_input.get_attribute('type')
                            input_name = associated_input.get_attribute('name')
                            input_value = associated_input.get_attribute('value')
                            
                            print(f"     Associated input: type={input_type}, name={input_name}, value={input_value}")
                            
                            if input_type == 'radio' and input_name == 'channelId':
                                print(f"     *** THIS IS THE TARGET RADIO BUTTON! ***")
                                
                        except Exception as e:
                            print(f"     Error finding associated input: {e}")
                            
            except Exception as e:
                print(f"   Label {i+1}: Error - {e}")
        
        # Method 4: Try to select The GRYD channel
        print(f"\n🎯 Method 4: Attempting to select '{config.RUMBLE_CHANNEL}'...")
        
        success = False
        
        # Try by label text
        try:
            for variation in channel_variations:
                try:
                    # Find label containing the channel name
                    label = uploader.driver.find_element("xpath", f"//label[contains(text(), '{variation}')]")
                    for_attr = label.get_attribute('for')
                    
                    if for_attr:
                        # Find the associated radio button
                        radio = uploader.driver.find_element("xpath", f"//input[@id='{for_attr}']")
                        
                        print(f"   Found radio for '{variation}' with id='{for_attr}'")
                        
                        # Try to select it with JavaScript
                        uploader.driver.execute_script("""
                            var radio = arguments[0];
                            radio.checked = true;
                            radio.dispatchEvent(new Event('change', { bubbles: true }));
                            radio.dispatchEvent(new Event('click', { bubbles: true }));
                        """, radio)
                        
                        # Verify selection
                        is_selected = radio.is_selected()
                        if is_selected:
                            print(f"   ✅ Successfully selected '{variation}' channel!")
                            success = True
                            break
                        else:
                            print(f"   ❌ Failed to select '{variation}' channel")
                            
                except Exception as e:
                    print(f"   Error with variation '{variation}': {e}")

                if success:
                    break
                
        except Exception as e:
            print(f"   Label method error: {e}")
        
        # Alternative: Try by radio button value
        if not success:
            print("\n🔄 Alternative: Try by radio button inspection...")
            
            for i, radio in enumerate(channel_radios):
                try:
                    # Get the radio button's context
                    parent = radio.find_element("xpath", "..")
                    context_text = parent.text.strip()
                    
                    print(f"   Radio {i+1} context: '{context_text}'")
                    
                    if any(var.lower() in context_text.lower() for var in channel_variations):
                        print(f"   Found target in context! Selecting...")
                        
                        uploader.driver.execute_script("""
                            var radio = arguments[0];
                            radio.checked = true;
                            radio.dispatchEvent(new Event('change', { bubbles: true }));
                            radio.dispatchEvent(new Event('click', { bubbles: true }));
                        """, radio)
                        
                        if radio.is_selected():
                            print(f"   ✅ Successfully selected channel via context!")
                            success = True
                            break
                        
                except Exception as e:
                    print(f"   Radio {i+1} context error: {e}")
        
        # Final verification
        print(f"\n📊 FINAL CHANNEL SELECTION STATUS:")
        
        for i, radio in enumerate(channel_radios):
            try:
                is_selected = radio.is_selected()
                value = radio.get_attribute('value')
                print(f"   Radio {i+1} (value={value}): {'✅ SELECTED' if is_selected else '❌ Not selected'}")
                
                if is_selected:
                    # Try to find the label for this selected radio
                    try:
                        id_attr = radio.get_attribute('id')
                        if id_attr:
                            label = uploader.driver.find_element("xpath", f"//label[@for='{id_attr}']")
                            label_text = label.text.strip()
                            print(f"     Selected channel: '{label_text}'")
                    except:
                        pass
                        
            except Exception as e:
                print(f"   Radio {i+1}: Error checking status - {e}")
        
        return success
        
    except Exception as e:
        print(f"❌ Debug error: {e}")
        return False
    
    finally:
        # Keep browser open for manual inspection
        if uploader and uploader.driver:
            response = input("\nKeep browser open for manual inspection? (y/N): ").strip().lower()
            if response in ['y', 'yes']:
                print("🔍 Browser open for manual inspection...")
                print("   Check the channel selection manually")
                print("   Look for 'The GRYD' option")
                print("   Close terminal when done")
                try:
                    while True:
                        time.sleep(10)
                except KeyboardInterrupt:
                    print("\n👋 Closing...")
            
            uploader.close()


def main():
    """Main function"""
    print("🧪 Channel Selection Debug Test")
    print("=" * 60)
    
    try:
        config.validate()
    except Exception as e:
        print(f"❌ Config error: {e}")
        return False
    
    print(f"🎯 Target channel: '{config.RUMBLE_CHANNEL}'")
    print("🔍 This test will:")
    print("   📺 Find all channel radio buttons")
    print("   🏷️ Analyze labels and associated inputs")
    print("   📄 Search page source for channel names")
    print("   🎯 Attempt to select the target channel")
    print("   ✅ Verify final selection")
    
    return debug_channel_selection()


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
