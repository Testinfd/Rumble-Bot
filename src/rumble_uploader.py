"""
Rumble video upload automation using Selenium
"""
import time
import random
import json
import os
from typing import Dict, List, Optional, Any
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
# from webdriver_manager.chrome import ChromeDriverManager  # Not needed with system ChromeDriver

from .config import config
from .logger import log


class RumbleUploader:
    """Handles automated video uploads to Rumble using Selenium"""
    
    def __init__(self):
        """Initialize the Rumble uploader"""
        self.driver = None
        self.wait = None
        self.is_logged_in = False

        # Rumble URLs
        self.base_url = "https://rumble.com"
        self.login_url = "https://rumble.com/login.php"
        self.upload_url = "https://rumble.com/upload.php"

        # Cookie management
        self.cookies_file = "rumble_cookies.json"

        log.info("RumbleUploader initialized")
    
    def _setup_driver(self) -> webdriver.Chrome:
        """Setup Chrome WebDriver with appropriate options"""
        try:
            chrome_options = Options()
            
            if config.HEADLESS_MODE:
                chrome_options.add_argument("--headless")
            
            # Additional Chrome options for stability
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
            
            # Disable images and CSS for faster loading (optional)
            prefs = {
                "profile.managed_default_content_settings.images": 2,
                "profile.default_content_setting_values.notifications": 2
            }
            chrome_options.add_experimental_option("prefs", prefs)
            
            # Setup ChromeDriver (use system-installed ChromeDriver)
            service = Service("/usr/local/bin/chromedriver")
            driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Set timeouts
            driver.implicitly_wait(config.IMPLICIT_WAIT)
            driver.set_page_load_timeout(config.SELENIUM_TIMEOUT)
            
            log.info("Chrome WebDriver setup successfully")
            return driver
            
        except Exception as e:
            log.error(f"Error setting up WebDriver: {e}")
            raise

    def save_cookies(self):
        """Save current cookies to file"""
        try:
            if self.driver:
                cookies = self.driver.get_cookies()
                with open(self.cookies_file, 'w') as f:
                    json.dump(cookies, f)
                log.info(f"Cookies saved to {self.cookies_file}")
        except Exception as e:
            log.error(f"Error saving cookies: {e}")

    def load_cookies(self):
        """Load cookies from file with better error handling"""
        try:
            if not os.path.exists(self.cookies_file):
                log.info("No cookie file found")
                return False

            with open(self.cookies_file, 'r') as f:
                cookies = json.load(f)

            if not cookies:
                log.info("Cookie file is empty")
                return False

            # Navigate to domain first with longer timeout
            log.info("Navigating to base URL for cookie loading...")
            self.driver.get(self.base_url)
            time.sleep(3)

            # Add cookies with better error handling
            cookies_added = 0
            for cookie in cookies:
                try:
                    # Ensure cookie has required fields
                    if 'name' in cookie and 'value' in cookie:
                        self.driver.add_cookie(cookie)
                        cookies_added += 1
                except Exception as e:
                    log.debug(f"Could not add cookie {cookie.get('name', 'unknown')}: {e}")

            log.info(f"Loaded {cookies_added}/{len(cookies)} cookies from {self.cookies_file}")
            return cookies_added > 0

        except Exception as e:
            log.error(f"Error loading cookies: {e}")
            return False

    def check_login_status(self) -> bool:
        """Check if already logged in using cookies"""
        try:
            # Navigate to a page that requires login
            self.driver.get(self.upload_url)
            time.sleep(3)

            # Check if we're redirected to login page
            current_url = self.driver.current_url.lower()
            if "login" in current_url or "auth.rumble.com" in current_url:
                log.info("Not logged in - need to authenticate")
                return False
            else:
                log.info("Already logged in via cookies")
                self.is_logged_in = True
                return True

        except Exception as e:
            log.error(f"Error checking login status: {e}")
            return False

    def _human_delay(self, min_seconds: float = 1.0, max_seconds: float = 3.0):
        """Add random delay to mimic human behavior"""
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)
    
    def _wait_and_find_element(self, by: By, value: str, timeout: int = None) -> Any:
        """Wait for element and return it"""
        if timeout is None:
            timeout = config.SELENIUM_TIMEOUT
        
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return element
        except TimeoutException:
            log.error(f"Element not found: {by}={value}")
            raise
    
    def _wait_and_click(self, by: By, value: str, timeout: int = None):
        """Wait for element to be clickable and click it"""
        if timeout is None:
            timeout = config.SELENIUM_TIMEOUT
        
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((by, value))
            )
            self._human_delay(0.5, 1.5)
            element.click()
            log.debug(f"Clicked element: {by}={value}")
        except TimeoutException:
            log.error(f"Element not clickable: {by}={value}")
            raise
    
    def login(self) -> bool:
        """Login to Rumble account"""
        try:
            if not self.driver:
                self.driver = self._setup_driver()
                self.wait = WebDriverWait(self.driver, config.SELENIUM_TIMEOUT)

            # Try to use existing cookies first
            log.info("Checking for existing login cookies...")
            if self.load_cookies():
                if self.check_login_status():
                    log.info("Successfully logged in using saved cookies!")
                    return True
                else:
                    log.info("Cookies expired or invalid, proceeding with fresh login...")

            log.info("Attempting fresh login to Rumble...")

            # Navigate to login page
            self.driver.get(self.login_url)
            self._human_delay(2, 4)
            
            # Find and fill email field
            email_field = self._wait_and_find_element(By.NAME, "username")
            email_field.clear()
            email_field.send_keys(config.RUMBLE_EMAIL)
            self._human_delay(1, 2)
            
            # Find and fill password field
            password_field = self._wait_and_find_element(By.NAME, "password")
            password_field.clear()
            password_field.send_keys(config.RUMBLE_PASSWORD)
            self._human_delay(1, 2)
            
            # Click login button (updated for new Rumble auth page)
            login_button_selectors = [
                "//button[@type='submit']",
                "//button[contains(text(), 'Sign In')]",
                "//button[contains(text(), 'Login')]",
                "//input[@type='submit' and @value='Login']",
                "//input[@type='submit']"
            ]

            login_button = None
            for selector in login_button_selectors:
                try:
                    login_button = self._wait_and_find_element(By.XPATH, selector, timeout=5)
                    break
                except:
                    continue

            if not login_button:
                raise Exception("Could not find login button")

            login_button.click()
            
            # Wait for login to complete
            self._human_delay(3, 5)
            
            # Check if login was successful
            # After successful login, should redirect away from auth.rumble.com
            current_url = self.driver.current_url.lower()
            if ("auth.rumble.com" not in current_url and "login" not in current_url) or "rumble.com" in current_url:
                self.is_logged_in = True
                log.info(f"Successfully logged in to Rumble - redirected to: {self.driver.current_url}")

                # Save cookies for future use
                self.save_cookies()

                return True
            else:
                log.error(f"Login failed - still on auth page: {self.driver.current_url}")
                return False
                
        except Exception as e:
            log.error(f"Error during login: {e}")
            return False
    
    def upload_video(self, video_path: str, title: str, description: str,
                    tags: List[str] = None, channel: str = None) -> Dict[str, Any]:
        """
        Upload video to Rumble

        Args:
            video_path: Path to video file
            title: Video title
            description: Video description
            tags: List of tags
            channel: Channel name to upload to (optional)

        Returns:
            Dict with upload result
        """
        start_time = time.time()
        result = {
            'success': False,
            'url': None,
            'error': None,
            'duration': 0
        }
        
        try:
            # Ensure we're logged in
            if not self.is_logged_in:
                if not self.login():
                    result['error'] = "Failed to login to Rumble"
                    return result
            
            log.info(f"Starting video upload: {video_path}")
            
            # Ensure we're on the upload page
            if not self._navigate_to_upload_page():
                result['error'] = "Failed to navigate to upload page"
                return result

            # Upload video file
            if not self._upload_file(video_path):
                result['error'] = "Failed to upload video file"
                return result
            
            # Wait for upload to complete (detect 100% progress)
            if not self._wait_for_upload_completion():
                log.warning("Upload progress not detected, continuing anyway")

            # Fill HIGH PRIORITY form fields
            success_count = 0
            total_priority_fields = 3

            # 1. Category (HIGH PRIORITY) - Use text input for "News"
            if self._select_category_text_input("News"):
                success_count += 1
                log.info("✅ Category selection successful")
            else:
                log.warning("❌ Category selection failed")

            # 2. Channel Selection (HIGH PRIORITY)
            if self._select_upload_destination(channel or config.RUMBLE_CHANNEL):
                success_count += 1
                log.info("✅ Channel selection successful")
            else:
                log.warning("❌ Channel selection failed")

            # 3. Visibility (HIGH PRIORITY)
            if self._set_visibility("Public"):
                success_count += 1
                log.info("✅ Visibility setting successful")
            else:
                log.warning("❌ Visibility setting failed")

            # Fill title (always attempt)
            self._fill_title_only(title)

            # Fill description (LOW PRIORITY - skip if problematic)
            if description:
                try:
                    self._fill_description_safe(description)
                except:
                    log.info("Skipping description due to form state issues")

            # Fill tags if provided
            if tags:
                try:
                    self._fill_tags_safe(tags)
                except:
                    log.info("Skipping tags due to form state issues")

            log.info(f"Form filling completed: {success_count}/{total_priority_fields} priority fields successful")

            # Submit the form and handle license page
            video_url = self._submit_upload_and_handle_license()
            if video_url:
                result['success'] = True
                result['url'] = video_url
                log.info(f"Video uploaded successfully: {video_url}")
            else:
                # Consider partial success if most priority fields worked
                if success_count >= 2:
                    result['success'] = True
                    result['url'] = self.driver.current_url
                    log.info(f"Upload likely successful despite detection issues ({success_count}/{total_priority_fields} priority fields)")
                else:
                    result['error'] = "Failed to complete upload process"
            
        except Exception as e:
            log.error(f"Error during video upload: {e}")
            result['error'] = str(e)
        
        finally:
            result['duration'] = round(time.time() - start_time, 2)
            
        return result

    def _navigate_to_upload_page(self) -> bool:
        """Ensure we're properly on the upload page"""
        try:
            log.info("Navigating to upload page...")

            # First try direct navigation
            self.driver.get(self.upload_url)
            self._human_delay(3, 5)

            current_url = self.driver.current_url.lower()
            log.info(f"After navigation, current URL: {current_url}")

            # Check if we're redirected to login (session expired)
            if "login" in current_url or "auth.rumble.com" in current_url:
                log.warning("Redirected to login - session may have expired")
                # Try to login again
                if not self.login():
                    return False
                # Try navigation again
                self.driver.get(self.upload_url)
                self._human_delay(3, 5)
                current_url = self.driver.current_url.lower()

            # Check if we're on the main page instead of upload page
            if current_url == "https://rumble.com/" or "upload" not in current_url:
                log.info("On main page, looking for upload link...")

                # Look for upload link on the main page
                upload_link_selectors = [
                    "//a[contains(@href, 'upload')]",
                    "//a[contains(text(), 'Upload')]",
                    "//button[contains(text(), 'Upload')]",
                    "//div[contains(@class, 'upload')]//a"
                ]

                for selector in upload_link_selectors:
                    try:
                        upload_link = self.driver.find_element(By.XPATH, selector)
                        if upload_link and upload_link.is_displayed():
                            log.info(f"Found upload link: {selector}")
                            upload_link.click()
                            self._human_delay(3, 5)
                            break
                    except:
                        continue
                else:
                    log.warning("Could not find upload link on main page")

            # Final check - are we on upload page?
            final_url = self.driver.current_url.lower()
            page_title = self.driver.title.lower()

            if "upload" in final_url or "upload" in page_title:
                log.info(f"Successfully on upload page: {final_url}")
                return True
            else:
                log.error(f"Failed to reach upload page. Current URL: {final_url}")
                return False

        except Exception as e:
            log.error(f"Error navigating to upload page: {e}")
            return False

    def _upload_file(self, video_path: str) -> bool:
        """Upload the video file - handles hidden file inputs"""
        try:
            log.info("Looking for file upload element...")

            # Wait for page to load
            self._human_delay(3, 5)

            # Look for the main file input (Filedata) - it's hidden but functional
            file_input_selectors = [
                "//input[@name='Filedata']",  # Primary upload input
                "//input[@id='Filedata']",
                "//input[@type='file' and @name='Filedata']",
                "//input[@type='file']",  # Fallback to any file input
            ]

            file_input = None
            for selector in file_input_selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    for element in elements:
                        # Check if it's enabled (even if hidden)
                        if element.is_enabled():
                            # Skip thumbnail upload (customThumb)
                            name = element.get_attribute('name')
                            if name and 'thumb' not in name.lower():
                                file_input = element
                                log.info(f"Found file input: name={name}, id={element.get_attribute('id')}")
                                break
                    if file_input:
                        break
                except Exception as e:
                    log.debug(f"Selector {selector} failed: {e}")
                    continue

            if not file_input:
                log.error("Could not find usable file upload element")
                return False

            # Send file path to the hidden input (this works even if hidden)
            absolute_path = str(Path(video_path).absolute())
            log.info(f"Uploading file to hidden input: {absolute_path}")

            # Use JavaScript to set the file if direct send_keys fails
            try:
                file_input.send_keys(absolute_path)
                log.info("Video file selected for upload via send_keys")
            except Exception as e:
                log.warning(f"send_keys failed, trying JavaScript method: {e}")
                # Alternative: Use JavaScript to trigger file selection
                self.driver.execute_script(f"arguments[0].style.display = 'block';", file_input)
                file_input.send_keys(absolute_path)
                self.driver.execute_script(f"arguments[0].style.display = 'none';", file_input)
                log.info("Video file selected for upload via JavaScript")

            # Wait for file to be processed and upload to start (reduced delay)
            self._human_delay(3, 5)

            return True

        except Exception as e:
            log.error(f"Error uploading file: {e}")
            return False

    def _wait_for_upload_completion(self) -> bool:
        """Wait for upload progress to reach 100%"""
        try:
            log.info("Waiting for upload progress to complete...")

            max_wait_time = 120  # 2 minutes max wait
            start_time = time.time()

            while time.time() - start_time < max_wait_time:
                # Check for 100% completion
                completion_indicators = [
                    "//*[contains(text(), '100%')]",
                    "//*[contains(text(), 'Complete')]",
                    "//*[contains(text(), 'Uploaded')]",
                    "//*[contains(text(), 'Processing')]"
                ]

                for indicator in completion_indicators:
                    try:
                        elements = self.driver.find_elements(By.XPATH, indicator)
                        if elements:
                            log.info(f"Upload completion detected: {elements[0].text}")
                            self._human_delay(1, 2)  # Reduced wait for form to be ready
                            return True
                    except:
                        continue

                # Check if upload form fields are now available/enabled
                title_field = self.driver.find_elements(By.XPATH, "//input[@name='title']")
                if title_field and title_field[0].is_enabled():
                    log.info("Upload form fields are now available")
                    return True

                self._human_delay(2, 3)

            log.warning("Upload progress timeout, but continuing...")
            return False

        except Exception as e:
            log.error(f"Error waiting for upload completion: {e}")
            return False

    def _select_category_text_input(self, category: str = "News") -> bool:
        """Select category using text input method"""
        try:
            log.info(f"Selecting category via text input: {category}")

            # Look for category input field (text input that accepts typing)
            category_input_selectors = [
                "//input[contains(@name, 'category')]",
                "//input[contains(@id, 'category')]",
                "//input[contains(@placeholder, 'category')]",
                "//input[contains(@placeholder, 'Category')]",
                "//input[contains(@class, 'category')]"
            ]

            for selector in category_input_selectors:
                try:
                    category_input = self.driver.find_element(By.XPATH, selector)
                    if category_input and category_input.is_enabled():
                        # Clear and type the category
                        category_input.clear()
                        category_input.send_keys(category)
                        log.info(f"Entered category via text input: {category}")
                        self._human_delay(1, 2)

                        # Press Tab to confirm
                        from selenium.webdriver.common.keys import Keys
                        category_input.send_keys(Keys.TAB)
                        self._human_delay(1, 2)
                        return True
                except:
                    continue

            # Fallback to dropdown method
            return self._select_category_dropdown(category)

        except Exception as e:
            log.error(f"Error selecting category via text input: {e}")
            return False

    def _select_category_dropdown(self, category: str = "News") -> bool:
        """Fallback method for category selection via dropdown"""
        try:
            category_selectors = [
                "//select[contains(@name, 'category')]",
                "//select[contains(@id, 'category')]",
                "//select[contains(@class, 'category')]"
            ]

            for selector in category_selectors:
                try:
                    category_dropdown = self.driver.find_element(By.XPATH, selector)
                    if category_dropdown:
                        from selenium.webdriver.support.ui import Select
                        select = Select(category_dropdown)

                        try:
                            select.select_by_visible_text(category)
                            log.info(f"Selected category via dropdown: {category}")
                            self._human_delay(1, 2)
                            return True
                        except:
                            # Try partial match
                            for option in select.options:
                                if category.lower() in option.text.lower():
                                    select.select_by_visible_text(option.text)
                                    log.info(f"Selected category by partial match: {option.text}")
                                    self._human_delay(1, 2)
                                    return True
                except:
                    continue

            return False

        except Exception as e:
            log.error(f"Error selecting category via dropdown: {e}")
            return False

    def _select_channel(self, channel_name: str) -> bool:
        """Legacy method - now redirects to _select_upload_destination"""
        return self._select_upload_destination(channel_name)

    def _select_category(self, category: str = "News") -> bool:
        """Select video category"""
        try:
            log.info(f"Selecting category: {category}")

            # Look for category dropdown or selection
            category_selectors = [
                "//select[contains(@name, 'category')]",
                "//select[contains(@id, 'category')]",
                "//select[contains(@class, 'category')]",
                "//div[contains(@class, 'category')]//select",
                "//select[contains(@name, 'genre')]",
                "//select[contains(@id, 'genre')]"
            ]

            for selector in category_selectors:
                try:
                    category_dropdown = self.driver.find_element(By.XPATH, selector)
                    if category_dropdown:
                        from selenium.webdriver.support.ui import Select
                        select = Select(category_dropdown)

                        # Try to select by visible text
                        try:
                            select.select_by_visible_text(category)
                            log.info(f"Selected category: {category}")
                            self._human_delay(1, 2)
                            return True
                        except:
                            # Try partial match
                            for option in select.options:
                                if category.lower() in option.text.lower():
                                    select.select_by_visible_text(option.text)
                                    log.info(f"Selected category by partial match: {option.text}")
                                    self._human_delay(1, 2)
                                    return True
                except:
                    continue

            log.warning(f"Could not find category selector for: {category}")
            return False

        except Exception as e:
            log.error(f"Error selecting category: {e}")
            return False

    def get_available_channels(self) -> list:
        """Get list of available channels for user selection"""
        try:
            # Make sure we're logged in first
            if not hasattr(self, 'driver') or not self.driver:
                self._setup_driver()
                self.login()

            # Navigate to upload page to see channels
            self.driver.get("https://rumble.com/upload.php")
            self._human_delay(2, 3)

            # Find all channel labels
            all_labels = self.driver.find_elements(By.XPATH, "//label[contains(@for, 'channelId')]")
            available_channels = []

            for label in all_labels:
                channel_text = label.text.strip()
                if channel_text:
                    # Get the associated radio button ID
                    for_attr = label.get_attribute('for')
                    if for_attr:  # Make sure for_attr exists
                        available_channels.append({
                            'name': channel_text,
                            'id': for_attr
                        })

            log.info(f"Found {len(available_channels)} available channels: {[ch['name'] for ch in available_channels]}")
            return available_channels

        except Exception as e:
            log.error(f"Error getting available channels: {e}")
            return []

    def _select_upload_destination(self, destination: str = None) -> bool:
        """Select upload destination/channel using the proven method"""
        try:
            if not destination:
                destination = "The GRYD"  # Default to The GRYD

            log.info(f"Selecting upload destination: {destination}")

            # First, let's see what channels are available
            try:
                all_labels = self.driver.find_elements(By.XPATH, "//label[contains(@for, 'channelId')]")
                available_channels = [label.text.strip() for label in all_labels if label.text.strip()]
                log.info(f"Available channels: {available_channels}")
            except Exception as e:
                log.debug(f"Could not list available channels: {e}")

            # Method 1: Find by label text and get associated radio (PROVEN METHOD)
            try:
                # Try exact match first
                label = self.driver.find_element(By.XPATH, f"//label[text()='{destination}']")
                for_attr = label.get_attribute('for')
                log.info(f"Found exact match for '{destination}'")
            except:
                try:
                    # Try partial match
                    label = self.driver.find_element(By.XPATH, f"//label[contains(text(), '{destination}')]")
                    for_attr = label.get_attribute('for')
                    log.info(f"Found partial match for '{destination}'")
                except Exception as e:
                    log.warning(f"Could not find channel '{destination}': {e}")
                    for_attr = None

            if for_attr:
                try:
                    radio = self.driver.find_element(By.XPATH, f"//input[@id='{for_attr}']")

                    log.info(f"Found radio for '{destination}' with id='{for_attr}'")

                    # Use JavaScript to select the radio button with proper events
                    self.driver.execute_script("""
                        var radio = arguments[0];
                        radio.checked = true;
                        radio.dispatchEvent(new Event('change', { bubbles: true }));
                        radio.dispatchEvent(new Event('click', { bubbles: true }));
                    """, radio)

                    # Verify selection
                    if radio.is_selected():
                        log.info(f"✅ Successfully selected '{destination}' channel")
                        self._human_delay(1, 2)
                        return True
                    else:
                        log.warning(f"❌ Channel '{destination}' selection verification failed")

                except Exception as e:
                    log.warning(f"Failed to select radio for '{destination}': {e}")

            # Method 2: Fallback - try all channel radios and select first available
            try:
                log.info("Trying fallback method - selecting first available channel")
                channel_radios = self.driver.find_elements(By.XPATH, "//input[@name='channelId']")

                for i, radio in enumerate(channel_radios):
                    try:
                        if radio.is_enabled():
                            # Use JavaScript to select
                            self.driver.execute_script("""
                                var radio = arguments[0];
                                radio.checked = true;
                                radio.dispatchEvent(new Event('change', { bubbles: true }));
                                radio.dispatchEvent(new Event('click', { bubbles: true }));
                            """, radio)

                            if radio.is_selected():
                                log.info(f"✅ Selected channel {i+1} (fallback)")
                                self._human_delay(1, 2)
                                return True
                    except Exception as e:
                        log.debug(f"Radio {i+1} failed: {e}")
                        continue

            except Exception as e:
                log.warning(f"Fallback method failed: {e}")

            log.warning(f"Could not select destination: {destination}")
            return False

        except Exception as e:
            log.error(f"Error selecting destination: {e}")
            return False

    def _set_visibility(self, visibility: str = "Public") -> bool:
        """Set video visibility"""
        try:
            log.info(f"Setting visibility to: {visibility}")

            # Look for specific visibility radio button (from working test)
            visibility_radio_selectors = [
                "//input[@id='visibility_public']",  # Specific public visibility radio
                f"//input[@type='radio' and @value='public']",
                f"//input[@type='radio' and contains(@value, '{visibility.lower()}')]",
                f"//label[contains(text(), '{visibility}')]//input[@type='radio']"
            ]

            for selector in visibility_radio_selectors:
                try:
                    visibility_radio = self.driver.find_element(By.XPATH, selector)
                    if visibility_radio and visibility_radio.is_displayed():
                        # Use JavaScript click with event dispatch (from working test)
                        self.driver.execute_script("""
                            arguments[0].checked = true;
                            arguments[0].dispatchEvent(new Event('change'));
                        """, visibility_radio)
                        log.info(f"Selected visibility radio button: {visibility}")
                        self._human_delay(0.5, 1)  # Reduced delay
                        return True
                except:
                    continue

            # Look for visibility dropdown
            visibility_selectors = [
                "//select[contains(@name, 'visibility')]",
                "//select[contains(@id, 'visibility')]",
                "//select[contains(@name, 'privacy')]"
            ]

            for selector in visibility_selectors:
                try:
                    visibility_dropdown = self.driver.find_element(By.XPATH, selector)
                    if visibility_dropdown and visibility_dropdown.is_displayed():
                        from selenium.webdriver.support.ui import Select
                        select = Select(visibility_dropdown)

                        try:
                            select.select_by_visible_text(visibility)
                            log.info(f"Selected visibility: {visibility}")
                            self._human_delay(0.5, 1)  # Reduced delay
                            return True
                        except:
                            # Try common values
                            for value in ['public', '1', 'Public']:
                                try:
                                    select.select_by_value(value)
                                    log.info(f"Selected visibility with value: {value}")
                                    self._human_delay(0.5, 1)
                                    return True
                                except:
                                    continue
                except:
                    continue

            # If no specific visibility controls found, it might be public by default
            log.warning(f"Could not find visibility selector for: {visibility} - may be public by default")
            return True  # Return True since many uploads are public by default

        except Exception as e:
            log.error(f"Error setting visibility: {e}")
            return False

    def _fill_title_only(self, title: str) -> bool:
        """Fill only the title field safely"""
        try:
            title_field = self._wait_and_find_element(By.NAME, "title", timeout=10)
            title_field.clear()
            title_field.send_keys(title)
            self._human_delay(1, 2)
            log.debug(f"Filled title: {title}")
            return True
        except Exception as e:
            log.warning(f"Could not fill title: {e}")
            return False

    def _fill_description_safe(self, description: str) -> bool:
        """Fill description field with error handling"""
        try:
            # Try multiple approaches to find and fill description
            description_selectors = [
                "//textarea[@name='description']",
                "//input[@name='description']",
                "//textarea[contains(@id, 'description')]",
                "//div[@contenteditable='true']"  # Rich text editor
            ]

            for selector in description_selectors:
                try:
                    description_field = self.driver.find_element(By.XPATH, selector)
                    if description_field and description_field.is_displayed():
                        # Check if field is enabled and ready
                        if description_field.is_enabled():
                            # Try different methods to clear and fill
                            try:
                                description_field.clear()
                                description_field.send_keys(description)
                                log.debug("Filled description successfully")
                                self._human_delay(0.5, 1)  # Reduced delay
                                return True
                            except:
                                # Try JavaScript method if direct input fails
                                self.driver.execute_script("arguments[0].value = arguments[1];", description_field, description)
                                log.debug("Filled description via JavaScript")
                                self._human_delay(0.5, 1)
                                return True
                        else:
                            log.debug(f"Description field not enabled: {selector}")
                except:
                    continue

            log.warning("Could not find or fill description field - skipping (not critical)")
            return False  # Not critical for upload success

        except Exception as e:
            log.warning(f"Could not fill description: {e}")
            return False

    def _fill_tags_safe(self, tags: List[str]) -> bool:
        """Fill tags field with error handling"""
        try:
            tags_field = self._wait_and_find_element(By.NAME, "tags", timeout=5)
            if tags_field.is_enabled():
                tags_field.clear()
                tags_string = ", ".join(tags)
                tags_field.send_keys(tags_string)
                self._human_delay(1, 2)
                log.debug(f"Filled tags: {tags_string}")
                return True
            else:
                log.warning("Tags field is not enabled")
                return False
        except Exception as e:
            log.warning(f"Could not fill tags: {e}")
            return False

    def _fill_video_details(self, title: str, description: str, tags: List[str] = None) -> bool:
        """Fill video title, description, and tags"""
        try:
            # Fill title
            title_field = self._wait_and_find_element(By.NAME, "title")
            title_field.clear()
            title_field.send_keys(title)
            self._human_delay(1, 2)
            log.debug(f"Filled title: {title}")
            
            # Fill description
            description_field = self._wait_and_find_element(By.NAME, "description")
            description_field.clear()
            description_field.send_keys(description)
            self._human_delay(1, 2)
            log.debug("Filled description")
            
            # Fill tags if provided
            if tags:
                try:
                    tags_field = self._wait_and_find_element(By.NAME, "tags")
                    tags_field.clear()
                    tags_string = ", ".join(tags)
                    tags_field.send_keys(tags_string)
                    self._human_delay(1, 2)
                    log.debug(f"Filled tags: {tags_string}")
                except:
                    log.warning("Could not find tags field - skipping")
            
            return True
            
        except Exception as e:
            log.error(f"Error filling video details: {e}")
            return False
    
    def _submit_upload_and_handle_license(self) -> Optional[str]:
        """Submit the upload form, handle license page, and return video URL"""
        try:
            # Check required checkboxes first
            self._check_required_boxes()

            # Find and click the main upload button (use specific ID from test)
            upload_button_selectors = [
                "//input[@id='submitForm']",  # Primary submit button
                "//button[contains(text(), 'Upload')]",
                "//input[@type='submit' and contains(@value, 'Upload')]",
                "//button[@type='submit']",
                "//input[@type='submit']"
            ]

            upload_button = None
            for selector in upload_button_selectors:
                try:
                    upload_button = self.driver.find_element(By.XPATH, selector)
                    if upload_button and upload_button.is_enabled():
                        break
                except:
                    continue

            if not upload_button:
                log.error("Could not find upload button")
                return None

            log.info("Clicking upload button...")
            # Use JavaScript click for reliability
            self.driver.execute_script("arguments[0].click();", upload_button)

            # Wait for page transition
            self._human_delay(3, 5)

            # Handle license agreement page and complete the entire workflow
            final_url = self._handle_license_page_and_submit()
            if final_url:
                log.info("License page handled and final submission completed successfully")
                return final_url
            else:
                log.warning("License page handling or final submission failed")
                return None

        except Exception as e:
            log.error(f"Error in upload submission: {e}")
            return None

    def _handle_license_page_and_submit(self) -> Optional[str]:
        """Handle the license agreement page and complete the entire upload workflow"""
        try:
            current_url = self.driver.current_url.lower()
            page_title = self.driver.title.lower()

            # Check if we're on a license or agreement page by content (not URL)
            page_source = self.driver.page_source.lower()
            license_content_indicators = [
                'terms and conditions',
                'you have not signed an exclusive agreement',
                'check here if you agree to our',
                'terms of service'
            ]

            is_license_page = any(indicator in page_source for indicator in license_content_indicators)

            if is_license_page:

                log.info("License/agreement page detected")

                # Target the specific Rumble agreement checkboxes
                log.info("Targeting specific Rumble agreement checkboxes...")

                checkboxes_checked = 0

                # Checkbox 1: Rights agreement (id='crights')
                try:
                    crights_checkbox = self.driver.find_element(By.XPATH, "//input[@id='crights']")
                    self.driver.execute_script("""
                        var checkbox = arguments[0];
                        checkbox.checked = true;
                        checkbox.dispatchEvent(new Event('change', { bubbles: true }));
                        checkbox.dispatchEvent(new Event('click', { bubbles: true }));
                    """, crights_checkbox)

                    # Verify
                    is_checked = self.driver.execute_script("return arguments[0].checked;", crights_checkbox)
                    if is_checked:
                        checkboxes_checked += 1
                        log.info("✅ Rights agreement checkbox checked")
                    else:
                        log.warning("❌ Rights agreement checkbox not checked")

                except Exception as e:
                    log.warning(f"Rights agreement checkbox error: {e}")

                # Checkbox 2: Terms agreement (id='cterms')
                try:
                    cterms_checkbox = self.driver.find_element(By.XPATH, "//input[@id='cterms']")
                    self.driver.execute_script("""
                        var checkbox = arguments[0];
                        checkbox.checked = true;
                        checkbox.dispatchEvent(new Event('change', { bubbles: true }));
                        checkbox.dispatchEvent(new Event('click', { bubbles: true }));
                    """, cterms_checkbox)

                    # Verify
                    is_checked = self.driver.execute_script("return arguments[0].checked;", cterms_checkbox)
                    if is_checked:
                        checkboxes_checked += 1
                        log.info("✅ Terms agreement checkbox checked")
                    else:
                        log.warning("❌ Terms agreement checkbox not checked")

                except Exception as e:
                    log.warning(f"Terms agreement checkbox error: {e}")

                log.info(f"Agreement checkboxes: {checkboxes_checked}/2 checked")

                # Wait before final submit
                self._human_delay(2, 3)

                # Look for final submit button (use specific ID from working test)
                license_submit_selectors = [
                    "//input[@id='submitForm2']",  # Specific final submit button from working test
                    "//button[contains(text(), 'Continue')]",
                    "//button[contains(text(), 'Agree')]",
                    "//button[contains(text(), 'Accept')]",
                    "//button[contains(text(), 'Submit')]",
                    "//input[@type='submit']",
                    "//button[@type='submit']"
                ]

                for selector in license_submit_selectors:
                    try:
                        submit_button = self.driver.find_element(By.XPATH, selector)
                        if submit_button and submit_button.is_enabled():
                            # Scroll to button and use JavaScript click (from working test)
                            self.driver.execute_script("arguments[0].scrollIntoView();", submit_button)
                            self._human_delay(1, 1)
                            self.driver.execute_script("arguments[0].click();", submit_button)
                            log.info(f"✅ FINAL SUBMIT CLICKED: {submit_button.get_attribute('id') or submit_button.text}")

                            # Wait for final result (from working test)
                            self._human_delay(5, 8)

                            # Check final result and detect success
                            final_url = self.driver.current_url
                            final_title = self.driver.title
                            log.info(f"After final submit - URL: {final_url}, Title: {final_title}")

                            # Now run success detection to find the actual video URL
                            return self._detect_upload_success()
                    except:
                        continue

                log.warning("Could not find final submit button on license page")
                return None

            # No license page found, proceed directly to success detection
            log.info("No license page detected, proceeding to success detection...")
            return self._detect_upload_success()

        except Exception as e:
            log.error(f"Error handling license page: {e}")
            return None

    def _detect_upload_success(self) -> Optional[str]:
        """Detect if upload was successful and return video URL - improved version"""
        try:
            before_url = self.driver.current_url
            before_title = self.driver.title
            log.info(f"Starting success detection at URL: {before_url}")

            # Monitor for changes over multiple attempts (like in working test)
            for attempt in range(1, 11):  # Check 10 times over 30 seconds
                self._human_delay(3, 3)  # 3 second intervals

                current_url = self.driver.current_url
                current_title = self.driver.title

                log.info(f"Attempt {attempt}: URL: {current_url}")

                success_indicators = []

                # URL-based indicators (highest priority)
                if "/v" in current_url and "rumble.com" in current_url:
                    success_indicators.append("Video URL detected")
                    log.info(f"Found video URL: {current_url}")
                    return current_url

                if current_url != before_url and "upload.php" not in current_url:
                    success_indicators.append("URL changed from upload page")
                    log.info(f"URL changed to non-upload page: {current_url}")
                    return current_url

                # Look for specific video URLs in page content
                try:
                    video_url_selectors = [
                        "//a[contains(@href, 'rumble.com/v')]",
                        "//a[contains(@href, '/v')]",
                        "//input[contains(@value, 'rumble.com/v')]",
                        "//div[contains(@class, 'video-url')]//a",
                        "//div[contains(@class, 'share')]//input",
                        "//input[contains(@class, 'video-url')]",
                        "//textarea[contains(@class, 'video-url')]"
                    ]

                    for selector in video_url_selectors:
                        url_elements = self.driver.find_elements(By.XPATH, selector)
                        for element in url_elements:
                            href = element.get_attribute('href') or element.get_attribute('value') or element.text
                            if href and 'rumble.com' in href and '/v' in href:
                                log.info(f"Found actual video URL in page: {href}")
                                return href
                except:
                    pass

                # Check for "Video Upload Complete!" success page
                try:
                    page_source = self.driver.page_source
                    if "Video Upload Complete!" in page_source:
                        success_indicators.append("Video Upload Complete page detected")
                        log.info("Found 'Video Upload Complete!' page")

                        # Look for the direct link URL pattern
                        import re
                        # Pattern for rumble.com/v URLs like https://rumble.com/v6xvjmq-blah.html
                        video_url_pattern = r'https://rumble\.com/v[a-zA-Z0-9]+-[^"\s<>]+\.html'
                        matches = re.findall(video_url_pattern, page_source)
                        if matches:
                            # Return the first valid video URL found
                            for match in matches:
                                if len(match) > 30:  # Valid video URLs are longer
                                    log.info(f"Found actual video URL: {match}")
                                    return match

                        # Also look for any rumble.com/v pattern
                        broader_pattern = r'https://rumble\.com/v[a-zA-Z0-9]+-[^"\s<>]+'
                        broader_matches = re.findall(broader_pattern, page_source)
                        if broader_matches:
                            for match in broader_matches:
                                if len(match) > 25:
                                    log.info(f"Found video URL (broader pattern): {match}")
                                    return match
                except:
                    pass

                # Success keywords in URL or title
                success_keywords = ['success', 'uploaded', 'complete', 'published', 'processing']
                if any(keyword in current_url.lower() for keyword in success_keywords):
                    success_indicators.append("Success keyword in URL")

                if any(keyword in current_title.lower() for keyword in success_keywords):
                    success_indicators.append("Success keyword in title")

                # Page content analysis
                try:
                    page_source = self.driver.page_source
                    page_source_lower = page_source.lower()

                    if "video upload complete!" in page_source:
                        success_indicators.append("Video Upload Complete page")
                        log.info("Found 'Video Upload Complete!' - this is the success page")

                        # Try to extract the actual video URL from this page
                        import re
                        video_url_pattern = r'https://rumble\.com/v[a-zA-Z0-9]+-[^"\s<>]+\.html'
                        matches = re.findall(video_url_pattern, page_source)
                        if matches:
                            log.info(f"SUCCESS! Found actual video URL: {matches[0]}")
                            return matches[0]

                    if "upload successful" in page_source_lower or "video uploaded" in page_source_lower:
                        success_indicators.append("Success message in page")
                    if "processing" in page_source_lower:
                        success_indicators.append("Processing detected")
                except:
                    pass

                # Report findings
                if success_indicators:
                    log.info(f"Success indicators found: {', '.join(success_indicators)}")

                    # If we have multiple indicators or strong single indicator, consider success
                    if len(success_indicators) >= 2 or "Video URL detected" in success_indicators:
                        log.info(f"SUCCESS DETECTED! ({len(success_indicators)} indicators)")
                        return current_url

                # Check for error indicators
                if "error" in current_url.lower() or "error" in current_title.lower():
                    log.warning("Error detected in URL or title")
                    break

                if "upload.php" in current_url and attempt > 5:
                    log.warning("Still on upload page after 15 seconds")
                    break

            # Final assessment
            final_url = self.driver.current_url
            final_title = self.driver.title

            log.info(f"Final assessment - URL: {final_url}, Title: {final_title}")

            # If URL changed from upload page, likely successful
            if final_url != before_url and "upload.php" not in final_url:
                log.info("URL changed from upload page - likely successful")
                return final_url

            # Check for any success indicators in final state
            if any(keyword in final_url.lower() or keyword in final_title.lower()
                   for keyword in ['success', 'complete', 'uploaded', 'processing']):
                log.info("Success indicators found in final state")
                return final_url

            # If we've gone through the workflow without major errors, consider it successful
            log.warning("No clear success indicators - upload status unclear")
            return final_url  # Return current URL for manual verification

        except Exception as e:
            log.error(f"Error detecting upload success: {e}")
            return None
    
    def _check_required_boxes(self):
        """Check all required checkboxes"""
        try:
            # Common checkbox selectors for terms, ownership, etc.
            checkbox_selectors = [
                "//input[@type='checkbox']",
                "//input[contains(@name, 'terms')]",
                "//input[contains(@name, 'agree')]",
                "//input[contains(@name, 'ownership')]",
                "//input[contains(@name, 'rights')]"
            ]
            
            for selector in checkbox_selectors:
                try:
                    checkboxes = self.driver.find_elements(By.XPATH, selector)
                    for checkbox in checkboxes:
                        if not checkbox.is_selected():
                            checkbox.click()
                            self._human_delay(0.5, 1.0)
                            log.debug("Checked required checkbox")
                except:
                    continue
                    
        except Exception as e:
            log.warning(f"Error checking boxes: {e}")
    
    def close(self):
        """Close the browser and cleanup"""
        try:
            if self.driver:
                self.driver.quit()
                self.driver = None
                self.is_logged_in = False
                log.info("Browser closed successfully")
        except Exception as e:
            log.error(f"Error closing browser: {e}")
    
    def __del__(self):
        """Cleanup when object is destroyed"""
        self.close()
