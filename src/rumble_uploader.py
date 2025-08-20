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
from webdriver_manager.chrome import ChromeDriverManager

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
            
            # Setup ChromeDriver
            service = Service(ChromeDriverManager().install())
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
        """Load cookies from file"""
        try:
            if os.path.exists(self.cookies_file):
                with open(self.cookies_file, 'r') as f:
                    cookies = json.load(f)

                # Navigate to domain first
                self.driver.get(self.base_url)
                time.sleep(2)

                # Add cookies
                for cookie in cookies:
                    try:
                        self.driver.add_cookie(cookie)
                    except Exception as e:
                        log.debug(f"Could not add cookie {cookie.get('name', 'unknown')}: {e}")

                log.info(f"Cookies loaded from {self.cookies_file}")
                return True
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
            
            # Navigate to upload page
            self.driver.get(self.upload_url)
            self._human_delay(2, 4)
            
            # Upload video file
            if not self._upload_file(video_path):
                result['error'] = "Failed to upload video file"
                return result
            
            # Fill video details first
            if not self._fill_video_details(title, description, tags):
                result['error'] = "Failed to fill video details"
                return result

            # Select category (default to News)
            if not self._select_category("News"):
                log.warning("Failed to select category, continuing anyway")

            # Select upload destination/channel
            if not self._select_upload_destination(channel or config.RUMBLE_CHANNEL):
                log.warning("Failed to select upload destination, continuing with default")

            # Set visibility to Public
            if not self._set_visibility("Public"):
                log.warning("Failed to set visibility, continuing anyway")

            # Submit the form and handle license page
            video_url = self._submit_upload_and_handle_license()
            if video_url:
                result['success'] = True
                result['url'] = video_url
                log.info(f"Video uploaded successfully: {video_url}")
            else:
                result['error'] = "Failed to complete upload process"
            
        except Exception as e:
            log.error(f"Error during video upload: {e}")
            result['error'] = str(e)
        
        finally:
            result['duration'] = round(time.time() - start_time, 2)
            
        return result
    
    def _upload_file(self, video_path: str) -> bool:
        """Upload the video file"""
        try:
            # Find file input element
            file_input = self._wait_and_find_element(By.XPATH, "//input[@type='file']")
            
            # Send file path to input
            file_input.send_keys(str(Path(video_path).absolute()))
            log.info("Video file selected for upload")
            
            # Wait for file to be processed
            self._human_delay(5, 10)
            
            # Wait for upload progress or completion indicator
            # This might vary based on Rumble's current UI
            try:
                # Look for upload progress or success indicator
                WebDriverWait(self.driver, 60).until(
                    lambda driver: "upload" not in driver.current_url.lower() or
                    driver.find_elements(By.XPATH, "//*[contains(text(), 'Upload complete')]") or
                    driver.find_elements(By.XPATH, "//*[contains(text(), 'Processing')]")
                )
            except TimeoutException:
                log.warning("Upload progress timeout - continuing anyway")
            
            return True
            
        except Exception as e:
            log.error(f"Error uploading file: {e}")
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

    def _select_upload_destination(self, destination: str = None) -> bool:
        """Select upload destination/channel"""
        try:
            if not destination:
                destination = "The GRYD"  # Default to The GRYD

            log.info(f"Selecting upload destination: {destination}")

            # Look for upload destination dropdown
            destination_selectors = [
                "//select[contains(@name, 'destination')]",
                "//select[contains(@name, 'channel')]",
                "//select[contains(@id, 'destination')]",
                "//select[contains(@id, 'channel')]",
                "//div[contains(@class, 'destination')]//select",
                "//div[contains(@class, 'channel')]//select"
            ]

            for selector in destination_selectors:
                try:
                    destination_dropdown = self.driver.find_element(By.XPATH, selector)
                    if destination_dropdown:
                        from selenium.webdriver.support.ui import Select
                        select = Select(destination_dropdown)

                        # Log available options
                        log.debug("Available destinations:")
                        for option in select.options:
                            log.debug(f"  - {option.text}")

                        # Try to select by visible text
                        try:
                            select.select_by_visible_text(destination)
                            log.info(f"Selected destination: {destination}")
                            self._human_delay(1, 2)
                            return True
                        except:
                            # Try partial match
                            for option in select.options:
                                if destination.lower() in option.text.lower():
                                    select.select_by_visible_text(option.text)
                                    log.info(f"Selected destination by partial match: {option.text}")
                                    self._human_delay(1, 2)
                                    return True
                except:
                    continue

            # Alternative: Look for destination buttons or radio buttons
            destination_button_selectors = [
                f"//input[@type='radio' and contains(@value, '{destination}')]",
                f"//label[contains(text(), '{destination}')]//input[@type='radio']",
                f"//div[contains(text(), '{destination}')]//input[@type='radio']"
            ]

            for selector in destination_button_selectors:
                try:
                    destination_radio = self.driver.find_element(By.XPATH, selector)
                    if destination_radio and not destination_radio.is_selected():
                        destination_radio.click()
                        log.info(f"Selected destination radio button: {destination}")
                        self._human_delay(1, 2)
                        return True
                except:
                    continue

            log.warning(f"Could not find destination selector for: {destination}")
            return False

        except Exception as e:
            log.error(f"Error selecting destination: {e}")
            return False

    def _set_visibility(self, visibility: str = "Public") -> bool:
        """Set video visibility"""
        try:
            log.info(f"Setting visibility to: {visibility}")

            # Look for visibility dropdown or radio buttons
            visibility_selectors = [
                "//select[contains(@name, 'visibility')]",
                "//select[contains(@id, 'visibility')]",
                "//select[contains(@name, 'privacy')]",
                "//select[contains(@id, 'privacy')]"
            ]

            for selector in visibility_selectors:
                try:
                    visibility_dropdown = self.driver.find_element(By.XPATH, selector)
                    if visibility_dropdown:
                        from selenium.webdriver.support.ui import Select
                        select = Select(visibility_dropdown)

                        try:
                            select.select_by_visible_text(visibility)
                            log.info(f"Selected visibility: {visibility}")
                            self._human_delay(1, 2)
                            return True
                        except:
                            # Try partial match
                            for option in select.options:
                                if visibility.lower() in option.text.lower():
                                    select.select_by_visible_text(option.text)
                                    log.info(f"Selected visibility by partial match: {option.text}")
                                    self._human_delay(1, 2)
                                    return True
                except:
                    continue

            # Look for radio buttons
            visibility_radio_selectors = [
                f"//input[@type='radio' and contains(@value, '{visibility.lower()}')]",
                f"//label[contains(text(), '{visibility}')]//input[@type='radio']",
                f"//input[@type='radio' and @value='public']" if visibility.lower() == "public" else None
            ]

            for selector in visibility_radio_selectors:
                if selector:
                    try:
                        visibility_radio = self.driver.find_element(By.XPATH, selector)
                        if visibility_radio and not visibility_radio.is_selected():
                            visibility_radio.click()
                            log.info(f"Selected visibility radio button: {visibility}")
                            self._human_delay(1, 2)
                            return True
                    except:
                        continue

            log.warning(f"Could not find visibility selector for: {visibility}")
            return False

        except Exception as e:
            log.error(f"Error setting visibility: {e}")
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

            # Find and click the main upload button
            upload_button_selectors = [
                "//button[contains(text(), 'Upload')]",
                "//input[@type='submit' and contains(@value, 'Upload')]",
                "//button[@type='submit']",
                "//input[@type='submit']",
                "//button[contains(@class, 'upload')]",
                "//div[contains(@class, 'upload-button')]//button"
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
            upload_button.click()

            # Wait for page transition
            self._human_delay(3, 5)

            # Handle license agreement page if it appears
            if self._handle_license_page():
                log.info("License page handled successfully")

            # Wait for upload processing
            log.info("Waiting for upload to complete...")
            self._human_delay(10, 15)

            # Try to detect successful upload
            return self._detect_upload_success()

        except Exception as e:
            log.error(f"Error in upload submission: {e}")
            return None

    def _handle_license_page(self) -> bool:
        """Handle the license agreement page that appears after upload"""
        try:
            current_url = self.driver.current_url.lower()
            page_title = self.driver.title.lower()

            # Check if we're on a license or agreement page
            if any(keyword in current_url for keyword in ['license', 'agreement', 'terms']) or \
               any(keyword in page_title for keyword in ['license', 'agreement', 'terms']):

                log.info("License/agreement page detected")

                # Look for agreement checkboxes
                agreement_checkboxes = self.driver.find_elements(By.XPATH,
                    "//input[@type='checkbox' and (contains(@name, 'license') or contains(@name, 'agreement') or contains(@name, 'terms'))]"
                )

                for checkbox in agreement_checkboxes:
                    if not checkbox.is_selected():
                        checkbox.click()
                        log.info("Checked license agreement checkbox")
                        self._human_delay(1, 2)

                # Look for continue/submit button on license page
                license_submit_selectors = [
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
                            submit_button.click()
                            log.info(f"Clicked license page submit button: {submit_button.text}")
                            self._human_delay(3, 5)
                            return True
                    except:
                        continue

                log.warning("Could not find submit button on license page")
                return False

            return True  # No license page found, which is fine

        except Exception as e:
            log.error(f"Error handling license page: {e}")
            return False

    def _detect_upload_success(self) -> Optional[str]:
        """Detect if upload was successful and return video URL"""
        try:
            current_url = self.driver.current_url
            log.info(f"Checking upload success at URL: {current_url}")

            # Wait a bit more for page to fully load
            self._human_delay(5, 8)

            # Look for success indicators
            success_indicators = [
                "//div[contains(text(), 'successfully')]",
                "//div[contains(text(), 'uploaded')]",
                "//div[contains(text(), 'complete')]",
                "//span[contains(text(), 'success')]",
                "//p[contains(text(), 'uploaded')]"
            ]

            for indicator in success_indicators:
                try:
                    elements = self.driver.find_elements(By.XPATH, indicator)
                    if elements:
                        log.info(f"Found success indicator: {elements[0].text}")
                        break
                except:
                    continue

            # Look for video URL in various places
            video_url_selectors = [
                "//a[contains(@href, 'rumble.com/v')]",
                "//a[contains(@href, '/v')]",
                "//input[contains(@value, 'rumble.com/v')]",
                "//div[contains(@class, 'video-url')]//a",
                "//div[contains(@class, 'share')]//a"
            ]

            for selector in video_url_selectors:
                try:
                    url_elements = self.driver.find_elements(By.XPATH, selector)
                    for element in url_elements:
                        href = element.get_attribute('href') or element.get_attribute('value')
                        if href and 'rumble.com' in href and '/v' in href:
                            log.info(f"Found video URL: {href}")
                            return href
                except:
                    continue

            # Check if we're redirected to a video page
            if '/v' in current_url and 'rumble.com' in current_url:
                log.info(f"Redirected to video page: {current_url}")
                return current_url

            # Check if we're on a success or confirmation page
            success_keywords = ['success', 'uploaded', 'complete', 'published']
            if any(keyword in current_url.lower() for keyword in success_keywords) or \
               any(keyword in self.driver.title.lower() for keyword in success_keywords):
                log.info("Upload appears successful based on page content")
                return current_url

            # If we can't find a specific video URL but upload seems successful
            log.warning("Could not find specific video URL, but upload may have succeeded")
            return current_url

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
