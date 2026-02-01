#!/bin/bash
# MinerU Auto-Converter Launcher
# Convenient script to start the converter

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=========================================="
echo "  MinerU Auto-Converter"
echo "=========================================="
echo ""

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3 first."
    echo "   Download from: https://www.python.org/downloads/"
    exit 1
fi

# Check if dependencies are installed
if ! python3 -c "import requests, watchdog" 2>/dev/null; then
    echo "📦 Installing dependencies..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install dependencies"
        exit 1
    fi
fi

# Check if API key is configured
if grep -q "YOUR_API_KEY_HERE" config.ini 2>/dev/null; then
    echo ""
    echo "⚠️  API key not configured!"
    echo ""
    echo "Please get your API key from: https://mineru.net/"
    echo "Then edit config.ini and replace YOUR_API_KEY_HERE"
    echo ""
    echo "Press any key to open config.ini in nano editor..."
    read -n 1
    nano config.ini
fi

echo ""
echo "🚀 Starting MinerU Auto-Converter..."
echo ""

python3 mineru_auto_converter.py
