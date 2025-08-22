# 🤖 Enhanced Rumble Bot - Large File Video Upload Assistant

An advanced Telegram bot that automatically uploads videos to Rumble with **large file support (up to 2GB)**, dynamic channel selection, intelligent metadata generation, and real-time progress tracking.

## ✨ Latest Features

### 📤 **Large File Support (NEW!)**
- **2GB File Uploads**: Handle large videos using Pyrogram integration
- **Hybrid Download System**: Pyrogram for large files + pyTelegramBotAPI fallback
- **Universal Media Support**: Video, document, audio, and photo uploads
- **Smart File Handling**: Automatic format detection and processing

### 🎯 **Dynamic Channel Management (NEW!)**
- **Auto Channel Discovery**: Automatically detects your available Rumble channels
- **Smart Selection Logic**: Auto-select from `RUMBLE_CHANNEL` env var or manual choice
- **Interactive Selection**: Shows numbered channel options when no env channel set
- **Multi-Account Support**: Works with any Rumble account's channels

### 🚀 **Core Functionality**
- **Automated Video Upload**: Upload videos to Rumble via Telegram
- **Real-time Progress Updates**: Step-by-step upload progress notifications
- **Actual URL Extraction**: Get real Rumble video URLs (not generic links)
- **Enhanced Error Handling**: Detailed error messages with actionable guidance
- **Robust Processing**: Optimized upload workflow with reduced delays (30-50% faster)

### 🎯 **Advanced Features**
- **Smart Metadata Generation**: AI-powered titles, descriptions, and tags
- **Optional Video Conversion**: FFmpeg integration for format compatibility
- **Configuration Management**: Bot-based environment variable management
- **Health Monitoring**: Built-in health check server
- **Comprehensive Logging**: Detailed logging for debugging and monitoring

### 📱 **Bot Commands**
- `/start` or `/help` - Show comprehensive help message with upload tips
- `/config` - **NEW!** Manage environment variables and bot configuration
- `/config status` - View current configuration and environment variables
- `/config set KEY "value"` - Set environment variables (e.g., RUMBLE_CHANNEL)
- `/config list` - List all configurable environment variables
- `/settings` - View current bot settings and feature toggles

## 📹 **How to Upload Large Videos**

### **For Large Files (>50 MB):**
1. In Telegram, tap the **📎 attachment** button
2. Choose **📄 File** (NOT 🎥 Video)
3. Select your video file
4. Send as document

### **Channel Selection:**
- **With RUMBLE_CHANNEL set**: Bot auto-selects your configured channel
- **Without RUMBLE_CHANNEL**: Bot shows available channels and waits for your choice
- **Dynamic Discovery**: Bot automatically finds your available Rumble channels

### **Supported Formats:**
- **Video**: MP4, AVI, MOV, MKV, and more
- **Size Limits**: Up to 2GB when sent as documents
- **Auto-Conversion**: Optional FFmpeg conversion for compatibility

## Quick Start

### Prerequisites

- Python 3.8+
- Chrome/Chromium browser
- Telegram Bot Token
- Rumble account
- **Telegram API Credentials** (for large file support)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd rumble-bot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Setup environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

4. **Run the bot**
   ```bash
   python main.py
   ```

## Configuration

### Required Environment Variables

```env
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here

# Telegram API Credentials (for large file support)
TELEGRAM_API_ID=your_api_id_from_my.telegram.org
TELEGRAM_API_HASH=your_api_hash_from_my.telegram.org

# Rumble Account Credentials
RUMBLE_EMAIL=your_rumble_email@example.com
RUMBLE_PASSWORD=your_rumble_password_here
```

### Optional Environment Variables

```env
# Channel Selection (optional - if not set, bot will show channel options)
RUMBLE_CHANNEL=your_preferred_channel_name

# Large File & Conversion Settings
MAX_FILE_SIZE_MB=2048
ENABLE_VIDEO_CONVERSION=false
```

### 🔑 **Getting Telegram API Credentials**

For large file support (up to 2GB), you need Telegram API credentials:

1. Go to https://my.telegram.org/auth
2. Log in with your phone number
3. Go to "API Development Tools"
4. Create an app:
   - **App title**: "Rumble Bot"
   - **Short name**: "rumblebot"
   - **Description**: "Video upload bot"
5. Copy your `api_id` (number) and `api_hash` (string)
6. Add them to your environment variables

### Additional Configuration

```env
# Bot Settings
MAX_FILE_SIZE_MB=2048
UPLOAD_TIMEOUT_SECONDS=1800
RETRY_ATTEMPTS=3

# Selenium Settings
HEADLESS_MODE=true
SELENIUM_TIMEOUT=30

# Random Content Generation
ENABLE_RANDOM_TITLES=true
ENABLE_RANDOM_DESCRIPTIONS=true
ENABLE_RANDOM_TAGS=true
```

## Usage

1. **Start the bot** by running `python main.py`
2. **Send a video** to your Telegram bot
3. **Optional**: Include title, description, or tags in the message
4. **Wait** for the bot to process and upload to Rumble
5. **Receive** confirmation with the Rumble video link

### Message Format

```
[Optional Title]

[Optional Description]

#tag1 #tag2 #tag3
```

## Deployment

### Heroku

1. Create a new Heroku app
2. Set environment variables in Heroku dashboard
3. Deploy using Git or GitHub integration

### Railway

1. Connect your GitHub repository
2. Set environment variables
3. Deploy automatically

### VPS/Local

1. Install dependencies
2. Setup systemd service (Linux) or Windows Service
3. Configure reverse proxy if needed

## Project Structure

```
rumble-bot/
├── src/
│   ├── __init__.py
│   ├── config.py          # Configuration management
│   ├── logger.py          # Logging setup
│   ├── telegram_bot.py    # Telegram bot implementation
│   ├── video_processor.py # Video download and processing
│   ├── rumble_uploader.py # Rumble automation
│   └── metadata_generator.py # Random content generation
├── logs/                  # Log files
├── downloads/            # Downloaded videos
├── temp/                 # Temporary files
├── main.py              # Entry point
├── requirements.txt     # Dependencies
├── .env.example        # Environment template
└── README.md           # This file
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is open-source and available under the MIT License.

## Disclaimer

This bot is for educational purposes. Ensure compliance with Telegram and Rumble terms of service. Use responsibly and respect platform guidelines.

## Support

For issues and questions, please open a GitHub issue or contact the maintainers.
