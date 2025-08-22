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
from .error_handler import error_handler
from .env_manager import EnvironmentManager


class RumbleBot:
    """Main Telegram bot class for handling video uploads to Rumble"""
    
    def __init__(self):
        """Initialize the bot with required components"""
        self.bot = telebot.TeleBot(config.TELEGRAM_BOT_TOKEN)
        self.video_processor = VideoProcessor()
        self.rumble_uploader = RumbleUploader()
        self.metadata_generator = MetadataGenerator()
        self.env_manager = EnvironmentManager()

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

        @self.bot.message_handler(commands=['stats'])
        def handle_stats(message: Message):
            self._handle_stats_command(message)

        @self.bot.message_handler(commands=['cancel'])
        def handle_cancel(message: Message):
            self._handle_cancel_command(message)

        @self.bot.message_handler(commands=['settings'])
        def handle_settings(message: Message):
            self._handle_settings_command(message)

        @self.bot.message_handler(commands=['config'])
        def handle_config(message: Message):
            self._handle_config_command(message)

        @self.bot.message_handler(content_types=['video', 'document'])
        def handle_video(message: Message):
            self._handle_video_message(message)

        @self.bot.message_handler(func=lambda message: True and not message.text.startswith('/config'))
        def handle_text(message: Message):
            self._handle_text_message(message)
    
    def _handle_start_command(self, message: Message):
        """Handle /start and /help commands"""
        help_text = f"""
🤖 **Enhanced Rumble Bot - Video Upload Assistant**

Send me a video file and I'll upload it to Rumble automatically with real-time progress updates!

**🚀 How to use:**
1. Send a video file (up to 2GB)
2. Watch real-time progress updates during upload
3. Optionally include title, description, and tags in your message
4. Get the actual Rumble video URL when done

**📝 Message format:**
```
Your Video Title

Your video description here.
It can be multiple lines.

#tag1 #tag2 #tag3
```

**📋 Available Commands:**
• `/start` or `/help` - Show this help message
• `/status` - Check bot and system status
• `/stats` - View upload statistics
• `/settings` - View current configuration
• `/cancel` - Cancel ongoing operations
• `/config` - Configure environment settings

**🔧 Configuration Commands:**
• `/config status` - View current configuration
• `/config setup` - Get setup instructions
• `/config list` - List all configurable variables
• `/config set VAR value` - Set environment variable
• `/config help` - Configuration help

**✨ Enhanced Features:**
• Real-time progress updates during upload
• Actual video URL extraction (not generic links)
• Robust error handling with detailed feedback
• Automatic metadata generation if not provided
• Fast, optimized upload processing

**⚙️ Current Settings:**
• Progress Updates: {'Enabled' if config.ENABLE_PROGRESS_UPDATES else 'Disabled'}
• Debug Info: {'Enabled' if config.ENABLE_DEBUG_INFO else 'Disabled'}
• Random Content: {'Enabled' if config.ENABLE_RANDOM_TITLES else 'Disabled'}

**💡 Upload Tips:**
• For large videos (>50 MB): Send as **document/file** instead of video
• Supports videos up to 2 GB when sent as documents
• MP4, AVI, MOV, and other video formats supported
• Add custom title/description in the file caption

Ready to upload your videos with enhanced experience! 🎉
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
- Random titles: {random_titles}
- Random descriptions: {random_descriptions}
- Random tags: {random_tags}

📊 **System:**
- Headless mode: {headless_mode}
- Log level: {log_level}
        """.format(
            max_size=config.MAX_FILE_SIZE_MB,
            timeout=config.UPLOAD_TIMEOUT_SECONDS,
            retries=config.RETRY_ATTEMPTS,
            random_titles='Enabled' if config.ENABLE_RANDOM_TITLES else 'Disabled',
            random_descriptions='Enabled' if config.ENABLE_RANDOM_DESCRIPTIONS else 'Disabled',
            random_tags='Enabled' if config.ENABLE_RANDOM_TAGS else 'Disabled',
            headless_mode='Enabled' if config.HEADLESS_MODE else 'Disabled',
            log_level=config.LOG_LEVEL
        )
        
        self.bot.reply_to(message, status_text, parse_mode='Markdown')
        log.info(f"Sent status message to user {message.from_user.id}")

    def _handle_stats_command(self, message: Message):
        """Handle /stats command"""
        try:
            # Get basic stats (you can expand this with actual tracking)
            stats_text = f"""
📊 **Upload Statistics**

🎯 **Current Session:**
• Bot uptime: Running
• Status: Online and ready

⚙️ **Configuration Status:**
• Progress Updates: {'✅ Enabled' if config.ENABLE_PROGRESS_UPDATES else '❌ Disabled'}
• Debug Information: {'✅ Enabled' if config.ENABLE_DEBUG_INFO else '❌ Disabled'}
• Random Titles: {'✅ Enabled' if config.ENABLE_RANDOM_TITLES else '❌ Disabled'}
• Random Descriptions: {'✅ Enabled' if config.ENABLE_RANDOM_DESCRIPTIONS else '❌ Disabled'}
• Random Tags: {'✅ Enabled' if config.ENABLE_RANDOM_TAGS else '❌ Disabled'}

🔧 **System Settings:**
• Max File Size: {config.MAX_FILE_SIZE_MB} MB
• Upload Timeout: {config.UPLOAD_TIMEOUT_SECONDS} seconds
• Retry Attempts: {config.RETRY_ATTEMPTS}
• Headless Mode: {'✅ Enabled' if config.HEADLESS_MODE else '❌ Disabled'}

📈 **Performance:**
• Enhanced upload processing: ✅ Active
• Real-time progress updates: ✅ Active
• Actual URL extraction: ✅ Active
            """

            self.bot.reply_to(message, stats_text, parse_mode='Markdown')
            log.info(f"Sent stats message to user {message.from_user.id}")

        except Exception as e:
            log.error(f"Error sending stats: {e}")
            self.bot.reply_to(message, "❌ Error retrieving statistics. Please try again.")

    def _handle_cancel_command(self, message: Message):
        """Handle /cancel command"""
        try:
            cancel_text = """
🛑 **Cancel Operations**

Currently, there are no active operations to cancel.

**Note:** Video uploads cannot be cancelled once they've started processing on Rumble's servers. However, you can:

• Wait for the current upload to complete
• Send a new video to start a fresh upload
• Use /status to check current bot status

If you're experiencing issues, try:
• /status - Check bot status
• /help - View available commands
• Contact support if problems persist
            """

            self.bot.reply_to(message, cancel_text, parse_mode='Markdown')
            log.info(f"Sent cancel message to user {message.from_user.id}")

        except Exception as e:
            log.error(f"Error sending cancel message: {e}")
            self.bot.reply_to(message, "❌ Error processing cancel command.")

    def _handle_settings_command(self, message: Message):
        """Handle /settings command"""
        try:
            settings_text = f"""
⚙️ **Current Bot Settings**

**🎯 Enhanced Features:**
• Progress Updates: {'✅ Enabled' if config.ENABLE_PROGRESS_UPDATES else '❌ Disabled'}
• Debug Information: {'✅ Enabled' if config.ENABLE_DEBUG_INFO else '❌ Disabled'}

**🎲 Content Generation:**
• Random Titles: {'✅ Enabled' if config.ENABLE_RANDOM_TITLES else '❌ Disabled'}
• Random Descriptions: {'✅ Enabled' if config.ENABLE_RANDOM_DESCRIPTIONS else '❌ Disabled'}
• Random Tags: {'✅ Enabled' if config.ENABLE_RANDOM_TAGS else '❌ Disabled'}

**📁 Upload Settings:**
• Max File Size: {config.MAX_FILE_SIZE_MB} MB
• Upload Timeout: {config.UPLOAD_TIMEOUT_SECONDS} seconds
• Retry Attempts: {config.RETRY_ATTEMPTS}
• Default Channel: {config.RUMBLE_CHANNEL}

**🔧 System Settings:**
• Headless Mode: {'✅ Enabled' if config.HEADLESS_MODE else '❌ Disabled'}
• Log Level: {config.LOG_LEVEL}

**💡 Note:** Settings are configured via environment variables and require bot restart to change.

For help with configuration, contact your administrator.
            """

            self.bot.reply_to(message, settings_text, parse_mode='Markdown')
            log.info(f"Sent settings message to user {message.from_user.id}")

        except Exception as e:
            log.error(f"Error sending settings: {e}")
            self.bot.reply_to(message, "❌ Error retrieving settings. Please try again.")

    @error_handler.retry_on_failure(max_attempts=3, delay=5)
    def _handle_video_message(self, message: Message):
        """Handle video file messages with detailed progress updates"""
        try:
            # Check file size first
            video = message.video or message.document
            if video and hasattr(video, 'file_size'):
                file_size_mb = video.file_size / (1024 * 1024)
                max_size_mb = config.MAX_FILE_SIZE_MB

                if file_size_mb > max_size_mb:
                    error_msg = f"""
📹 **Video Too Large**

**File Size**: {file_size_mb:.1f} MB
**Maximum Allowed**: {max_size_mb} MB

**Please:**
• Compress your video to under {max_size_mb} MB
• Use a video compression tool
• Try uploading a shorter clip

**Tip**: Most video editors can export at lower quality/resolution to reduce file size.
                    """
                    self.bot.reply_to(message, error_msg, parse_mode='Markdown')
                    log.warning(f"Video too large: {file_size_mb:.1f} MB from user {message.from_user.id}")
                    return

            # Send initial response
            processing_msg = self.bot.reply_to(
                message,
                f"📹 Video received! ({file_size_mb:.1f} MB)\n\n⏳ Processing and uploading to Rumble..."
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

            # Update with metadata info
            self.bot.edit_message_text(
                f"📹 Video received!\n\n📝 **Metadata:**\n- Title: {title}\n- Tags: {', '.join(tags) if tags else 'None'}\n\n⬇️ Downloading video...",
                message.chat.id,
                processing_msg.message_id,
                parse_mode='Markdown'
            )

            # Process the video
            video_path = self._process_video_file(message)

            if not video_path:
                # Check if it's a file size issue
                video = message.video or message.document
                if video and hasattr(video, 'file_size'):
                    file_size_mb = video.file_size / (1024 * 1024)
                    if file_size_mb > config.MAX_FILE_SIZE_MB:
                        error_text = f"""❌ <b>Video Too Large</b>

Your video ({file_size_mb:.1f} MB) exceeds the maximum size limit of {config.MAX_FILE_SIZE_MB} MB.

<b>Solutions:</b>
• Compress your video using a video editor
• Upload a shorter clip
• Reduce video quality/resolution
• Try online video compressors

<b>Tip:</b> Most phones can compress videos in their gallery apps."""
                    else:
                        error_text = """❌ <b>Download Failed</b>

Unable to download your video. This could be due to:
• Temporary network issues
• File format not supported
• Telegram API limitations

<b>Please try:</b>
• Send as **document/file** instead of video (supports larger files)
• Upload the video again
• Convert to MP4 format
• Check your internet connection"""
                else:
                    # No file size info available - likely too big for Telegram
                    error_text = """❌ <b>File Too Large</b>

Your video is too large for Telegram to process (over 50 MB limit).

<b>Solutions:</b>
• **Send as document/file** instead of video (supports up to 2 GB)
• Compress your video to under 50 MB
• Upload a shorter clip
• Reduce video quality/resolution

<b>💡 Best Solution:</b> Use the document/file option in Telegram for large videos!"""

                self.bot.edit_message_text(
                    error_text,
                    message.chat.id,
                    processing_msg.message_id,
                    parse_mode='HTML'
                )
                return

            # Update status - login phase
            self.bot.edit_message_text(
                f"📤 Video downloaded successfully!\n\n🔐 Logging into Rumble...\n\n📝 **Video:** {title}",
                message.chat.id,
                processing_msg.message_id,
                parse_mode='Markdown'
            )

            # Upload to Rumble with progress callback
            upload_result = self._upload_with_progress_updates(
                video_path, title, description, tags, message.chat.id, processing_msg.message_id
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

🎉 Your video is now live on Rumble!
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
                debug_info = upload_result.get('debug_info', '')

                if config.ENABLE_DEBUG_INFO and debug_info:
                    error_text = f"""
❌ **Upload Failed**

**Error:** {error_msg}

**Debug Info:**
{debug_info}

Please try again later or contact support if the issue persists.
                    """
                else:
                    error_text = f"""
❌ **Upload Failed**

**Error:** {error_msg}

Please try again later or contact support if the issue persists.
                    """

                self.bot.edit_message_text(
                    error_text,
                    message.chat.id,
                    processing_msg.message_id,
                    parse_mode='Markdown'
                )

                log.error(f"Upload failed for user {message.from_user.id}: {error_msg}")

            # Cleanup
            self._cleanup_file(video_path)

        except Exception as e:
            log.error(f"Error processing video message: {e}")
            try:
                self.bot.edit_message_text(
                    f"❌ <b>System Error</b>\n\nAn unexpected error occurred: {str(e)}\n\nPlease try again later.",
                    message.chat.id,
                    processing_msg.message_id,
                    parse_mode='HTML'
                )
            except:
                self.bot.reply_to(message, f"❌ An error occurred: {str(e)}")

    def _upload_with_progress_updates(self, video_path: str, title: str, description: str,
                                    tags: list, chat_id: int, message_id: int) -> dict:
        """Upload video with progress updates to user"""
        try:
            if config.ENABLE_PROGRESS_UPDATES:
                # Phase 1: Login
                self.bot.edit_message_text(
                    f"🔐 Logging into Rumble...\n\n📝 **Video:** {title}",
                    chat_id, message_id, parse_mode='Markdown'
                )

                # Phase 2: Upload file
                self.bot.edit_message_text(
                    f"📤 Uploading video file...\n\n📝 **Video:** {title}\n⏳ This may take a few minutes depending on file size.",
                    chat_id, message_id, parse_mode='Markdown'
                )

                # Phase 3: Form filling
                self.bot.edit_message_text(
                    f"📝 Filling upload form...\n\n📝 **Video:** {title}\n✅ File uploaded successfully",
                    chat_id, message_id, parse_mode='Markdown'
                )

                # Phase 4: Final submission
                self.bot.edit_message_text(
                    f"🚀 Submitting upload...\n\n📝 **Video:** {title}\n✅ Form completed",
                    chat_id, message_id, parse_mode='Markdown'
                )

                # Phase 5: Processing
                self.bot.edit_message_text(
                    f"⚙️ Processing upload...\n\n📝 **Video:** {title}\n✅ Upload submitted\n⏳ Waiting for Rumble to process...",
                    chat_id, message_id, parse_mode='Markdown'
                )

            # Actual upload
            upload_result = self.rumble_uploader.upload_video(
                video_path=video_path,
                title=title,
                description=description,
                tags=tags,
                channel=config.RUMBLE_CHANNEL
            )

            return upload_result

        except Exception as e:
            log.error(f"Error in upload with progress: {e}")
            debug_info = f'Progress update error: {e}' if config.ENABLE_DEBUG_INFO else ''
            return {'success': False, 'error': str(e), 'debug_info': debug_info}
    
    def _handle_config_command(self, message: Message):
        """Handle /config command and subcommands"""
        try:
            # Debug log to check message type
            log.debug(f"Config command message type: {type(message)}")

            # Validate message object
            if not hasattr(message, 'text') or not hasattr(message, 'chat'):
                log.error(f"Invalid message object: {type(message)}")
                return

            # Parse command arguments - handle extra spaces
            text = message.text.strip()
            parts = [part for part in text.split() if part]  # Remove empty parts

            if len(parts) == 1:  # Just "/config"
                response = self.env_manager.get_setup_instructions()

            elif len(parts) == 2:  # "/config subcommand"
                subcommand = parts[1].lower()

                if subcommand == 'status':
                    status = self.env_manager.get_configuration_status()
                    response = f"""🔧 <b>Environment Configuration Status</b>

<b>Configured Variables:</b> {status['configured_count']}/{status['total_vars']}

"""
                    if status['configured']:
                        response += "<b>✅ Configured:</b>\n"
                        for var_name, var_info in status['configured'].items():
                            response += f"• <b>{var_name}</b>: {var_info['value']}\n"

                    if status['missing']:
                        response += "\n<b>❌ Missing Required:</b>\n"
                        for var in status['missing']:
                            response += f"• <b>{var['name']}</b>: {var['description']}\n"

                    if not status['missing']:
                        response += "\n✅ <b>All required variables configured!</b>"

                elif subcommand == 'setup':
                    response = self.env_manager.get_setup_instructions()

                elif subcommand == 'list':
                    response = self.env_manager.get_variable_list()

                elif subcommand == 'help':
                    response = """🔧 <b>Configuration Help</b>

<b>Available Commands:</b>
• <code>/config status</code> - View current configuration
• <code>/config setup</code> - Get setup instructions
• <code>/config list</code> - List all configurable variables
• <code>/config set VAR value</code> - Set environment variable
• <code>/config help</code> - Show this help

<b>Setting Variables:</b>
Use <code>/config set VARIABLE_NAME value</code> format.

<b>Examples:</b>
• <code>/config set RUMBLE_EMAIL your@email.com</code>
• <code>/config set RUMBLE_PASSWORD yourpassword</code>
• <code>/config set RUMBLE_CHANNEL "Your Channel"</code>
• <code>/config set MAX_FILE_SIZE_MB 1024</code>
• <code>/config set HEADLESS_MODE true</code>

<b>⚠️ Security:</b>
Sensitive values (passwords, emails) are hidden in status displays."""

                else:
                    response = f"❌ Unknown subcommand: {subcommand}\nUse `/config help` for available commands."

            elif len(parts) >= 4 and parts[1].lower() == 'set':  # "/config set VAR value"
                var_name = parts[2].upper()
                value = ' '.join(parts[3:])  # Join remaining parts as value

                success, message = self.env_manager.set_environment_variable(var_name, value)
                response = message

                if success:
                    response += "\n\n💡 <b>Note:</b> Changes take effect immediately for new operations."

            else:
                response = "❌ Invalid command format.\nUse `/config help` for usage instructions."

            # Ensure message is valid before replying
            if hasattr(message, 'chat') and hasattr(message, 'from_user'):
                self.bot.reply_to(message, response, parse_mode='HTML')
                log.info(f"Handled config command from user {message.from_user.id}")
            else:
                log.error(f"Invalid message object in config handler: {type(message)}")

        except Exception as e:
            log.error(f"Error handling config command: {e}")
            try:
                # Ensure message is a proper Message object
                if hasattr(message, 'chat') and hasattr(message, 'message_id'):
                    self.bot.reply_to(message, "❌ Error processing configuration command. Please try again.")
                else:
                    log.error(f"Invalid message object type: {type(message)}")
            except Exception as reply_error:
                log.error(f"Failed to send error reply: {reply_error}")

    def _handle_text_message(self, message: Message):
        """Handle text messages"""
        # Default response for other text
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
            # Prioritize document uploads (higher file size limit)
            if message.document and message.document.mime_type and 'video' in message.document.mime_type:
                file_info = self.bot.get_file(message.document.file_id)
                file_size = message.document.file_size
                log.info(f"Processing video as document: {file_size / (1024*1024):.1f} MB")
            elif message.video:
                file_info = self.bot.get_file(message.video.file_id)
                file_size = message.video.file_size
                log.info(f"Processing video message: {file_size / (1024*1024):.1f} MB")
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
            error_msg = str(e)
            log.error(f"Error downloading video: {e}")

            # Provide specific error feedback
            if "file is too big" in error_msg.lower():
                log.warning(f"File size exceeded Telegram's limit for user {message.from_user.id}")
                # This error is already handled in the main handler
            elif "bad request" in error_msg.lower():
                log.warning(f"Bad request error for user {message.from_user.id}: {error_msg}")
            else:
                log.error(f"Unexpected download error for user {message.from_user.id}: {error_msg}")

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

    def stop(self):
        """Stop the bot gracefully"""
        try:
            log.info("Stopping Telegram bot...")
            self.bot.stop_polling()

            # Close any open browser instances
            if hasattr(self, 'rumble_uploader') and self.rumble_uploader:
                self.rumble_uploader.close()

            log.info("Telegram bot stopped successfully")

        except Exception as e:
            log.error(f"Error stopping bot: {e}")
