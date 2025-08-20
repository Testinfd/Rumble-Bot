"""
Rumble video upload automation using Selenium
"""
import time
import random
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
            
            log.info("Attempting to login to Rumble...")
            
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
            
            # Click login button
            login_button = self._wait_and_find_element(By.XPATH, "//input[@type='submit' and @value='Login']")
            login_button.click()
            
            # Wait for login to complete
            self._human_delay(3, 5)
            
            # Check if login was successful
            if "login" not in self.driver.current_url.lower():
                self.is_logged_in = True
                log.info("Successfully logged in to Rumble")
                return True
            else:
                log.error("Login failed - still on login page")
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
            
            # Select channel if specified
            if not self._select_channel(channel or config.RUMBLE_CHANNEL):
                log.warning("Failed to select channel, continuing with default")

            # Fill video details
            if not self._fill_video_details(title, description, tags):
                result['error'] = "Failed to fill video details"
                return result
            
            # Submit the form
            video_url = self._submit_upload()
            if video_url:
                result['success'] = True
                result['url'] = video_url
                log.info(f"Video uploaded successfully: {video_url}")
            else:
                result['error'] = "Failed to submit upload"
            
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
        """Select the channel to upload to"""
        if not channel_name:
            log.debug("No channel specified, using default")
            return True

        try:
            log.info(f"Attempting to select channel: {channel_name}")

            # Look for channel dropdown or selection
            channel_selectors = [
                "//select[contains(@name, 'channel')]",
                "//select[contains(@id, 'channel')]",
                "//select[contains(@class, 'channel')]",
                "//div[contains(@class, 'channel-select')]//select",
                "//div[contains(@class, 'channel-dropdown')]//select"
            ]

            for selector in channel_selectors:
                try:
                    channel_dropdown = self.driver.find_element(By.XPATH, selector)
                    if channel_dropdown:
                        # Try to select by visible text
                        from selenium.webdriver.support.ui import Select
                        select = Select(channel_dropdown)

                        # Try different ways to select the channel
                        try:
                            select.select_by_visible_text(channel_name)
                            log.info(f"Selected channel by visible text: {channel_name}")
                            self._human_delay(1, 2)
                            return True
                        except:
                            try:
                                select.select_by_value(channel_name)
                                log.info(f"Selected channel by value: {channel_name}")
                                self._human_delay(1, 2)
                                return True
                            except:
                                # Try partial match
                                for option in select.options:
                                    if channel_name.lower() in option.text.lower():
                                        select.select_by_visible_text(option.text)
                                        log.info(f"Selected channel by partial match: {option.text}")
                                        self._human_delay(1, 2)
                                        return True
                except:
                    continue

            # Alternative: Look for channel buttons or links
            channel_button_selectors = [
                f"//button[contains(text(), '{channel_name}')]",
                f"//a[contains(text(), '{channel_name}')]",
                f"//div[contains(text(), '{channel_name}')][@role='button']",
                f"//span[contains(text(), '{channel_name}')]/parent::*[@role='button']"
            ]

            for selector in channel_button_selectors:
                try:
                    channel_button = self.driver.find_element(By.XPATH, selector)
                    if channel_button and channel_button.is_enabled():
                        channel_button.click()
                        log.info(f"Selected channel by clicking button: {channel_name}")
                        self._human_delay(1, 2)
                        return True
                except:
                    continue

            log.warning(f"Could not find channel selector for: {channel_name}")
            return False

        except Exception as e:
            log.error(f"Error selecting channel: {e}")
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
    
    def _submit_upload(self) -> Optional[str]:
        """Submit the upload form and return video URL"""
        try:
            # Check required checkboxes
            self._check_required_boxes()
            
            # Find and click submit button
            submit_button = self._wait_and_find_element(
                By.XPATH, 
                "//input[@type='submit'] | //button[contains(text(), 'Upload')] | //button[contains(text(), 'Submit')]"
            )
            submit_button.click()
            log.info("Clicked submit button")
            
            # Wait for submission to complete
            self._human_delay(5, 10)
            
            # Try to get the video URL from the result page
            try:
                # Look for success message or video URL
                # This will need to be adjusted based on Rumble's actual response
                video_url_element = WebDriverWait(self.driver, 30).until(
                    lambda driver: driver.find_elements(By.XPATH, "//a[contains(@href, 'rumble.com/v')]")
                )
                
                if video_url_element:
                    video_url = video_url_element[0].get_attribute('href')
                    return video_url
                
            except TimeoutException:
                log.warning("Could not find video URL - upload may still be processing")
            
            # Return current URL as fallback
            return self.driver.current_url
            
        except Exception as e:
            log.error(f"Error submitting upload: {e}")
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
