# Rumble Bot Setup Guide

This guide will help you set up and deploy the Rumble Bot for automated video uploads.

## Prerequisites

### Required
- Python 3.8 or higher
- Chrome/Chromium browser
- Telegram Bot Token (from @BotFather)
- Rumble account with upload permissions

### Optional
- Docker (for containerized deployment)
- Git (for version control)

## Step 1: Get Telegram Bot Token

1. Open Telegram and search for `@BotFather`
2. Start a chat and send `/newbot`
3. Follow the instructions to create your bot
4. Save the bot token (looks like `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)
5. Get your chat ID by messaging your bot and visiting:
   `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`

## Step 2: Prepare Rumble Account

1. Create a Rumble account at https://rumble.com
2. Verify your email address
3. Ensure you have upload permissions
4. Note your login email and password

## Step 3: Local Installation

### Option A: Automatic Installation (Linux/macOS)

```bash
# Clone the repository
git clone <repository-url>
cd rumble-bot

# Run installation script
chmod +x scripts/install.sh
./scripts/install.sh

# Configure environment
nano .env
```

### Option B: Manual Installation

```bash
# Clone the repository
git clone <repository-url>
cd rumble-bot

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create directories
mkdir -p logs downloads temp

# Copy environment file
cp .env.example .env
```

## Step 4: Configuration

Edit the `.env` file with your credentials:

```env
# Required Settings
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
RUMBLE_EMAIL=your_rumble_email@example.com
RUMBLE_PASSWORD=your_rumble_password_here

# Optional Settings
MAX_FILE_SIZE_MB=2048
HEADLESS_MODE=true
LOG_LEVEL=INFO
RETRY_ATTEMPTS=3
```

## Step 5: Testing

### Run Tests
```bash
# Activate virtual environment
source venv/bin/activate

# Run tests
python tests/run_tests.py
```

### Test Bot Locally
```bash
# Development mode (with browser visible)
./scripts/dev.sh

# Production mode (headless)
./scripts/run.sh
```

## Step 6: Cloud Deployment

### Option A: Railway

1. Fork this repository to your GitHub
2. Sign up at https://railway.app
3. Connect your GitHub account
4. Create new project from GitHub repo
5. Set environment variables in Railway dashboard:
   - `TELEGRAM_BOT_TOKEN`
   - `RUMBLE_EMAIL`
   - `RUMBLE_PASSWORD`
6. Deploy automatically

### Option B: Render

1. Fork this repository to your GitHub
2. Sign up at https://render.com
3. Create new Web Service
4. Connect your GitHub repo
5. Use these settings:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python main.py`
6. Set environment variables in Render dashboard
7. Deploy

### Option C: Heroku

1. Install Heroku CLI
2. Login to Heroku: `heroku login`
3. Create app: `heroku create your-app-name`
4. Set environment variables:
   ```bash
   heroku config:set TELEGRAM_BOT_TOKEN=your_token
   heroku config:set RUMBLE_EMAIL=your_email
   heroku config:set RUMBLE_PASSWORD=your_password
   ```
5. Deploy: `git push heroku main`

### Option D: VPS/Server

```bash
# Install on Ubuntu/Debian server
sudo apt update
sudo apt install python3 python3-pip python3-venv git

# Clone and setup
git clone <repository-url>
cd rumble-bot
./scripts/install.sh

# Create systemd service
sudo nano /etc/systemd/system/rumble-bot.service
```

Service file content:
```ini
[Unit]
Description=Rumble Bot
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/rumble-bot
Environment=PATH=/path/to/rumble-bot/venv/bin
ExecStart=/path/to/rumble-bot/venv/bin/python main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable rumble-bot
sudo systemctl start rumble-bot
sudo systemctl status rumble-bot
```

## Step 7: Docker Deployment

### Build and Run Locally
```bash
# Build image
docker build -t rumble-bot .

# Run container
docker run -d \
  --name rumble-bot \
  -e TELEGRAM_BOT_TOKEN=your_token \
  -e RUMBLE_EMAIL=your_email \
  -e RUMBLE_PASSWORD=your_password \
  -v $(pwd)/logs:/app/logs \
  rumble-bot
```

### Using Docker Compose
```bash
# Copy environment file
cp .env.example .env
# Edit .env with your credentials

# Start services
docker-compose up -d

# View logs
docker-compose logs -f
```

## Troubleshooting

### Common Issues

1. **Chrome/ChromeDriver Issues**
   ```bash
   # Update ChromeDriver
   pip install --upgrade webdriver-manager
   ```

2. **Permission Errors**
   ```bash
   # Fix permissions
   chmod +x scripts/*.sh
   sudo chown -R $USER:$USER logs downloads temp
   ```

3. **Memory Issues**
   - Increase server memory
   - Enable headless mode
   - Reduce file size limits

4. **Network Issues**
   - Check firewall settings
   - Verify internet connection
   - Use VPN if needed

### Logs and Monitoring

```bash
# View logs
tail -f logs/rumble_bot.log

# Check bot status
curl http://localhost:8080/health

# Monitor with Docker
docker logs -f rumble-bot
```

### Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `TELEGRAM_BOT_TOKEN` | Yes | - | Bot token from @BotFather |
| `RUMBLE_EMAIL` | Yes | - | Rumble account email |
| `RUMBLE_PASSWORD` | Yes | - | Rumble account password |
| `MAX_FILE_SIZE_MB` | No | 2048 | Maximum file size in MB |
| `HEADLESS_MODE` | No | true | Run browser in headless mode |
| `LOG_LEVEL` | No | INFO | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `RETRY_ATTEMPTS` | No | 3 | Number of retry attempts |
| `SELENIUM_TIMEOUT` | No | 30 | Selenium timeout in seconds |

## Security Notes

- Never commit `.env` file to version control
- Use strong passwords for Rumble account
- Enable 2FA on Rumble if available
- Regularly rotate credentials
- Monitor logs for suspicious activity
- Use HTTPS for webhook URLs

## Support

For issues and questions:
1. Check the logs first
2. Review this setup guide
3. Search existing GitHub issues
4. Create a new issue with logs and details

## Next Steps

After successful setup:
1. Test with a small video file
2. Monitor logs for any issues
3. Set up monitoring/alerting
4. Consider backup strategies
5. Plan for scaling if needed
