#!/bin/bash

# Rumble Bot Installation Script

echo "🤖 Installing Rumble Bot..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

# Check Python version
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python $python_version is installed, but Python $required_version+ is required."
    exit 1
fi

echo "✅ Python $python_version detected"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Create directories
echo "📁 Creating directories..."
mkdir -p logs downloads temp

# Copy environment file
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo "⚠️ Please edit .env file with your credentials before running the bot"
else
    echo "✅ .env file already exists"
fi

# Make scripts executable
chmod +x scripts/*.sh

echo "🎉 Installation complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your credentials:"
echo "   nano .env"
echo ""
echo "2. Run the bot:"
echo "   ./scripts/run.sh"
echo ""
echo "3. Or run in development mode:"
echo "   ./scripts/dev.sh"
