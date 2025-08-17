# macOS Live Subtitles Overlay - Setup Guide

## 🚀 Quick Setup (Automated)

### Option 1: Run the setup script

```bash
# Make the script executable
chmod +x setup_env.sh

# Run the automated setup
./setup_env.sh
```

### Option 2: Manual setup

```bash
# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install BlackHole 2ch
brew install blackhole-2ch

# Create virtual environment
python3 -m venv venv

# Activate environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## 🎵 Audio Configuration

### Step 1: Create Multi-Output Device

1. Open **Audio MIDI Setup** (Applications → Utilities → Audio MIDI Setup)
2. Click the **+** button → **Create Multi-Output Device**
3. Check both:
   - **BlackHole 2ch**
   - Your real speakers/headphones
4. Name it something like "System + BlackHole"

### Step 2: Set System Output

1. Open **System Settings** → **Sound** → **Output**
2. Select your **Multi-Output Device** (e.g., "System + BlackHole")
3. Test by playing audio - you should hear sound AND it should be captured

## 🐍 Using the Virtual Environment

### Activate Environment

```bash
source venv/bin/activate
# or use the quick script:
./activate_env.sh
```

### Run Application

```bash
python live_subs_mac.py
```

### Deactivate Environment

```bash
deactivate
```

## 🔧 Troubleshooting

### Common Issues

#### "BlackHole device not found"

- Ensure BlackHole 2ch is installed: `brew install blackhole-2ch`
- Check Audio MIDI Setup for BlackHole 2ch device
- Restart Audio MIDI Setup if needed

#### "No module named 'sounddevice'"

- Ensure virtual environment is activated: `source venv/bin/activate`
- Reinstall dependencies: `pip install -r requirements.txt`

#### "ASR model not available"

- The app will try faster-whisper first, then fall back to openai-whisper
- Both should work, but faster-whisper is preferred for performance

#### Audio not being captured

- Verify Multi-Output Device is selected in System Sound settings
- Check that BlackHole 2ch is enabled in the Multi-Output Device
- Try restarting the application

### Performance Tips

- **Apple Silicon Macs**: faster-whisper works great on CPU
- **Intel Macs**: Consider using smaller models like "tiny.en" or "base.en"
- **Memory**: Models use ~1-2GB RAM depending on size

## 📱 Application Controls

- **Font Size**: `+` / `-` keys
- **Opacity**: `[` / `]` keys
- **Clear**: `C` key
- **Quit**: `Q` or `Esc` key
- **Move**: Drag the window to reposition

## 🗂️ Project Structure

```
├── live_subs_mac.py      # Main application
├── requirements.txt       # Python dependencies
├── setup_env.sh          # Automated setup script
├── activate_env.sh       # Quick activation script
├── README_SETUP.md       # This setup guide
└── README_mac_live_subs.md  # Original project README
```

## 🔄 Updating Dependencies

```bash
# Activate environment
source venv/bin/activate

# Update all packages
pip install --upgrade -r requirements.txt

# Or update specific packages
pip install --upgrade faster-whisper sounddevice
```

## 🆘 Getting Help

If you encounter issues:

1. Check the troubleshooting section above
2. Ensure all prerequisites are installed
3. Verify audio configuration is correct
4. Check that virtual environment is activated
5. Review error messages in terminal output
