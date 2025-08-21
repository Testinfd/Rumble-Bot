#!/bin/bash

# Enhanced Rumble Bot - Render Build Script
echo "🚀 Building Enhanced Rumble Bot for Render..."

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements-render.txt

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p downloads logs processed temp

echo "✅ Build completed successfully!"
echo "🎉 Enhanced Rumble Bot ready for deployment!"
