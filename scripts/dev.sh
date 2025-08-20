#!/bin/bash

# Rumble Bot Development Script

echo "🛠️ Starting Rumble Bot in development mode..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run install.sh first."
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found. Please copy .env.example to .env and configure it."
    exit 1
fi

# Set development environment variables
export LOG_LEVEL=DEBUG
export HEADLESS_MODE=false

# Create directories if they don't exist
mkdir -p logs downloads temp

# Run the bot with development settings
echo "🚀 Launching bot in development mode..."
echo "📊 Log level: DEBUG"
echo "🖥️ Headless mode: Disabled"
echo ""
python main.py
