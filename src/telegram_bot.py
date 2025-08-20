"""
Telegram Bot implementation for Rumble video uploads
"""
import os
import re
import time
from typing import Optional, Tuple, List
import telebot
from telebot.types import Message
from pathlib import Path

from .config import config
from .logger import log
from .video_processor import VideoProcessor
from .rumble_uploader import RumbleUploader
from .metadata_generator import MetadataGenerator
from .error_handler import error_handler, RetryableError, NonRetryableError, format_error_message


class RumbleBot:
    """Main Telegram bot class for handling video uploads to Rumble"""
    
    def __init__(self):
        """Initialize the bot with required components"""
        self.bot = telebot.TeleBot(config.TELEGRAM_BOT_TOKEN)
        self.video_processor = VideoProcessor()
        self.rumble_uploader = RumbleUploader()
        self.metadata_generator = MetadataGenerator()
        
        # Setup message handlers
        self._setup_handlers()
        
        log.info("RumbleBot initialized successfully")
    
    def _setup_handlers(self):
        """Setup message handlers for the bot"""
        
        @self.bot.message_handler(commands=['start', 'help'])
        def handle_start(message: Message):
            self._handle_start_command(message)
        
        @self.bot.message_handler(commands=['status'])
        def handle_status(message: Message):
            self._handle_status_command(message)
        
        @self.bot.message_handler(content_types=['video', 'document'])
        def handle_video(message: Message):
            self._handle_video_message(message)
        
        @self.bot.message_handler(func=lambda message: True)
        def handle_text(message: Message):
            self._handle_text_message(message)
    
    def _handle_start_command(self, message: Message):
        """Handle /start and /help commands"""
        help_text = """
🤖 **Rumble Bot - Video Upload Assistant**

Send me a video file and I'll upload it to Rumble automatically!

**How to use:**
1. Send a video file (up to 2GB)
2. Optionally include title, description, and tags in your message
3. Wait for the upload to complete
4. Receive the Rumble video link

**Message format:**
```
Your Video Title

Your video description here.
It can be multiple lines.

#tag1 #tag2 #tag3
```

**Commands:**
/start - Show this help message
/status - Check bot status
/help - Show this help message

**Note:** If you don't provide title/description/tags, I'll generate random ones for you!
        """
        
        self.bot.reply_to(message, help_text, parse_mode='Markdown')
        log.info(f"Sent help message to user {message.from_user.id}")
    
    def _handle_status_command(self, message: Message):
        """Handle /status command"""
        status_text = """
✅ **Bot Status: Online**

🔧 **Configuration:**
- Max file size: {max_size} MB
- Upload timeout: {timeout} seconds
- Retry attempts: {retries}
- Random titles: {'Enabled' if config.ENABLE_RANDOM_TITLES else 'Disabled'}
- Random descriptions: {'Enabled' if config.ENABLE_RANDOM_DESCRIPTIONS else 'Disabled'}
- Random tags: {'Enabled' if config.ENABLE_RANDOM_TAGS else 'Disabled'}

📊 **System:**
- Headless mode: {'Enabled' if config.HEADLESS_MODE else 'Disabled'}
- Log level: {log_level}
        """.format(
            max_size=config.MAX_FILE_SIZE_MB,
            timeout=config.UPLOAD_TIMEOUT_SECONDS,
            retries=config.RETRY_ATTEMPTS,
            log_level=config.LOG_LEVEL
        )
        
        self.bot.reply_to(message, status_text, parse_mode='Markdown')
        log.info(f"Sent status message to user {message.from_user.id}")
    
    @error_handler.retry_on_failure(max_attempts=3, delay=5)
    def _handle_video_message(self, message: Message):
        """Handle video file messages"""
        try:
            # Send initial response
            processing_msg = self.bot.reply_to(
                message, 
                "📹 Video received! Processing and uploading to Rumble...\n\n⏳ This may take a few minutes."
            )
            
            # Extract metadata from message text
            title, description, tags = self._extract_metadata(message.caption or "")
            
            # Generate random metadata if needed
            if not title and config.ENABLE_RANDOM_TITLES:
                title = self.metadata_generator.generate_title()
            
            if not description and config.ENABLE_RANDOM_DESCRIPTIONS:
                description = self.metadata_generator.generate_description()
            
            if not tags and config.ENABLE_RANDOM_TAGS:
                tags = self.metadata_generator.generate_tags()
            
            log.info(f"Processing video from user {message.from_user.id}")
            log.info(f"Metadata - Title: {title}, Description: {description[:50]}..., Tags: {tags}")
            
            # Process the video
            video_path = self._process_video_file(message)
            
            if not video_path:
                self.bot.edit_message_text(
                    "❌ Failed to download video. Please try again.",
                    message.chat.id,
                    processing_msg.message_id
                )
                return
            
            # Update status
            self.bot.edit_message_text(
                "📤 Video downloaded successfully! Uploading to Rumble...",
                message.chat.id,
                processing_msg.message_id
            )
            
            # Upload to Rumble
            upload_result = self.rumble_uploader.upload_video(
                video_path=video_path,
                title=title,
                description=description,
                tags=tags
            )
            
            if upload_result.get('success'):
                success_text = f"""
✅ **Upload Successful!**

📹 **Video Details:**
- Title: {title}
- Description: {description[:100]}{'...' if len(description) > 100 else ''}
- Tags: {', '.join(tags) if tags else 'None'}

🔗 **Rumble Link:** {upload_result.get('url', 'Processing...')}

⏱️ **Upload Time:** {upload_result.get('duration', 'Unknown')} seconds
                """
                
                self.bot.edit_message_text(
                    success_text,
                    message.chat.id,
                    processing_msg.message_id,
                    parse_mode='Markdown'
                )
                
                log.info(f"Successfully uploaded video for user {message.from_user.id}")
            else:
                error_msg = upload_result.get('error', 'Unknown error occurred')
                self.bot.edit_message_text(
                    f"❌ Upload failed: {error_msg}\n\nPlease try again later.",
                    message.chat.id,
                    processing_msg.message_id
                )
                
                log.error(f"Upload failed for user {message.from_user.id}: {error_msg}")
            
            # Cleanup
            self._cleanup_file(video_path)
            
        except Exception as e:
            log.error(f"Error processing video message: {e}")
            self.bot.reply_to(message, f"❌ An error occurred: {str(e)}")
    
    def _handle_text_message(self, message: Message):
        """Handle text messages"""
        self.bot.reply_to(
            message,
            "📹 Please send a video file to upload to Rumble.\n\nUse /help for more information."
        )
    
    def _extract_metadata(self, text: str) -> Tuple[Optional[str], Optional[str], List[str]]:
        """Extract title, description, and tags from message text"""
        if not text:
            return None, None, []
        
        lines = text.strip().split('\n')
        title = None
        description_lines = []
        tags = []
        
        # Extract hashtags
        tag_pattern = r'#(\w+)'
        for line in lines:
            found_tags = re.findall(tag_pattern, line)
            tags.extend(found_tags)
            # Remove hashtags from the line for further processing
            line_without_tags = re.sub(tag_pattern, '', line).strip()
            if line_without_tags:
                if title is None:
                    title = line_without_tags
                else:
                    description_lines.append(line_without_tags)
        
        description = '\n'.join(description_lines).strip() if description_lines else None
        
        return title, description, tags
    
    def _process_video_file(self, message: Message) -> Optional[str]:
        """Process and download video file"""
        try:
            if message.video:
                file_info = self.bot.get_file(message.video.file_id)
                file_size = message.video.file_size
            elif message.document and message.document.mime_type and 'video' in message.document.mime_type:
                file_info = self.bot.get_file(message.document.file_id)
                file_size = message.document.file_size
            else:
                log.warning("Unsupported file type received")
                return None
            
            # Check file size
            max_size_bytes = config.MAX_FILE_SIZE_MB * 1024 * 1024
            if file_size and file_size > max_size_bytes:
                log.warning(f"File too large: {file_size} bytes")
                return None
            
            # Download file
            downloaded_file = self.bot.download_file(file_info.file_path)
            
            # Save to downloads directory
            file_extension = Path(file_info.file_path).suffix or '.mp4'
            filename = f"video_{int(time.time())}{file_extension}"
            file_path = Path(config.DOWNLOADS_DIR) / filename
            
            with open(file_path, 'wb') as f:
                f.write(downloaded_file)
            
            log.info(f"Video downloaded successfully: {file_path}")
            return str(file_path)
            
        except Exception as e:
            log.error(f"Error downloading video: {e}")
            return None
    
    def _cleanup_file(self, file_path: str):
        """Clean up downloaded file"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                log.info(f"Cleaned up file: {file_path}")
        except Exception as e:
            log.warning(f"Failed to cleanup file {file_path}: {e}")
    
    def start(self):
        """Start the bot"""
        log.info("Starting Telegram bot polling...")
        self.bot.infinity_polling(timeout=10, long_polling_timeout=5)
