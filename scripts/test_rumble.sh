#!/bin/bash

# Rumble Upload Test Script

echo "🧪 Testing Rumble Upload Functionality..."

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

# Set test environment variables
export LOG_LEVEL=DEBUG
export HEADLESS_MODE=false  # Show browser for testing

echo "🔧 Test Configuration:"
echo "   - Log level: DEBUG"
echo "   - Headless mode: Disabled (browser will be visible)"
echo "   - Make sure your Rumble credentials are set in .env"
echo ""

# Run the test
python test_rumble_upload.py
