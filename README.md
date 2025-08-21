# 🤖 Enhanced Rumble Bot - Automated Video Upload Assistant

An advanced Telegram bot that automatically uploads videos to Rumble with real-time progress updates, enhanced error handling, and actual video URL extraction.

## ✨ Enhanced Features

### 🚀 Core Functionality
- **Automated Video Upload**: Upload videos to Rumble via Telegram
- **Real-time Progress Updates**: Step-by-step upload progress notifications
- **Actual URL Extraction**: Get real Rumble video URLs (not generic links)
- **Enhanced Error Handling**: Detailed error messages with actionable guidance
- **Robust Processing**: Optimized upload workflow with reduced delays (30-50% faster)

### 🎯 Advanced Features
- **Smart Metadata Generation**: Automatic titles, descriptions, and tags
- **Multiple Upload Formats**: Support for various video formats
- **Graceful Shutdown**: Proper resource cleanup and process management
- **Health Monitoring**: Built-in health check server
- **Comprehensive Logging**: Detailed logging for debugging and monitoring

### 📱 Enhanced Bot Commands
- `/start` or `/help` - Show comprehensive help message
- `/status` - Check bot and system status
- `/stats` - View upload statistics and configuration
- `/settings` - View current bot settings
- `/cancel` - Cancel ongoing operations (where possible)

## Quick Start

### Prerequisites

- Python 3.8+
- Chrome/Chromium browser
- Telegram Bot Token
- Rumble account

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

# Rumble Account Credentials
RUMBLE_EMAIL=your_rumble_email@example.com
RUMBLE_PASSWORD=your_rumble_password_here
RUMBLE_CHANNEL=your_channel_name_here
```

### Optional Configuration

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
