#!/bin/bash

# Rumble Bot Run Script

echo "🤖 Starting Rumble Bot..."

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

# Create directories if they don't exist
mkdir -p logs downloads temp

# Run the bot
echo "🚀 Launching bot..."
python main.py
