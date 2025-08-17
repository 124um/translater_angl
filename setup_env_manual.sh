#!/bin/bash

# macOS Live Subtitles Overlay - Manual Environment Setup Script
# Use this when you don't have sudo access for BlackHole installation

set -e  # Exit on any error

echo "🚀 Setting up macOS Live Subtitles Overlay environment (Manual Mode)..."

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

# Try to install BlackHole 2ch
echo "🎵 Attempting to install BlackHole 2ch virtual audio device..."
if brew install blackhole-2ch; then
    echo "✅ BlackHole 2ch installed successfully"
    echo "⚠️  You may need to reboot for BlackHole to take effect"
else
    echo "⚠️  BlackHole 2ch installation failed (likely due to permissions)"
    echo ""
    echo "📋 Manual BlackHole Installation Required:"
    echo "1. Download BlackHole 2ch manually:"
    echo "   https://existential.audio/blackhole/"
    echo "2. Install the .pkg file"
    echo "3. Restart your Mac"
    echo "4. Continue with this script after restart"
    echo ""
    read -p "Press Enter to continue with Python setup, or Ctrl+C to exit..."
fi

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
echo "🎉 Python environment setup completed!"
echo ""
echo "📋 Next steps:"
echo "1. Ensure BlackHole 2ch is installed and working:"
echo "   - Check Audio MIDI Setup for BlackHole 2ch device"
echo "   - If not visible, restart your Mac"
echo ""
echo "2. Configure audio:"
echo "   - Open Audio MIDI Setup"
echo "   - Create Multi-Output Device with BlackHole 2ch + your speakers"
echo "   - Set System Output to your Multi-Output Device"
echo ""
echo "3. Activate environment:"
echo "   source venv/bin/activate"
echo ""
echo "4. Run the application:"
echo "   python live_subs_mac.py"
echo ""
echo "5. Deactivate environment when done:"
echo "   deactivate" 