#!/bin/bash

# Quick activation script for the virtual environment
echo "🔧 Activating Python virtual environment..."
source venv/bin/activate
echo "✅ Virtual environment activated!"
echo "🐍 Python path: $(which python)"
echo "📦 Pip path: $(which pip)"
echo ""
echo "🚀 You can now run: python live_subs_mac.py"
echo "🔚 To deactivate: deactivate" 