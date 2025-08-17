#!/bin/bash

# macOS Live Subtitles Overlay - Environment Setup Script
# This script sets up the Python virtual environment and installs all dependencies

set -e  # Exit on any error

echo "🚀 Setting up macOS Live Subtitles Overlay environment..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    echo "   Visit: https://www.python.org/downloads/"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "✅ Python version: $PYTHON_VERSION"

# Check if Homebrew is installed
if ! command -v brew &> /dev/null; then
    echo "📦 Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    echo "✅ Homebrew installed successfully"
else
    echo "✅ Homebrew is already installed"
fi

# Install BlackHole 2ch
echo "🎵 Installing BlackHole 2ch virtual audio device..."
brew install blackhole-2ch
echo "✅ BlackHole 2ch installed successfully"

# Create virtual environment
echo "🐍 Creating Python virtual environment..."
python3 -m venv venv
echo "✅ Virtual environment created"

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📚 Installing Python dependencies..."
pip install -r requirements.txt

echo ""
echo "🎉 Environment setup completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Configure audio:"
echo "   - Open Audio MIDI Setup"
echo "   - Create Multi-Output Device with BlackHole 2ch + your speakers"
echo "   - Set System Output to your Multi-Output Device"
echo ""
echo "2. Activate environment:"
echo "   source venv/bin/activate"
echo ""
echo "3. Run the application:"
echo "   python live_subs_mac.py"
echo ""
echo "4. Deactivate environment when done:"
echo "   deactivate" 