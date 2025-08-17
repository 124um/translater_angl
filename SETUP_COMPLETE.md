# 🎉 Environment Setup Complete!

## ✅ What's Been Installed

- **Python Virtual Environment**: `venv/` directory
- **Core Dependencies**:
  - `sounddevice` - Audio capture
  - `numpy` - Numerical processing
  - `faster-whisper` - Speech recognition (primary engine)

## ⚠️ BlackHole 2ch Still Needed

The Python environment is ready, but you still need to install **BlackHole 2ch** manually:

### Option 1: Manual Download & Install

1. Visit: https://existential.audio/blackhole/
2. Download the latest `.pkg` file
3. Double-click to install
4. **Restart your Mac** (required for audio drivers)

### Option 2: Ask Admin for Sudo Access

If you have an administrator account, they can run:

```bash
brew install blackhole-2ch
```

## 🚀 Next Steps

### 1. Install BlackHole 2ch (see above)

### 2. Configure Audio (after BlackHole installation)

1. Open **Audio MIDI Setup** (Applications → Utilities)
2. Click **+** → **Create Multi-Output Device**
3. Check both:
   - **BlackHole 2ch**
   - Your real speakers/headphones
4. In **System Settings → Sound → Output**, select your Multi-Output Device

### 3. Test the Application

```bash
# Activate environment
source venv/bin/activate

# Run the app
python live_subs_mac.py
```

### 4. Application Controls

- **Font Size**: `+` / `-` keys
- **Opacity**: `[` / `]` keys
- **Clear**: `C` key
- **Quit**: `Q` or `Esc` key
- **Move**: Drag window to reposition

## 🔧 Environment Management

### Activate Environment

```bash
source venv/bin/activate
```

### Deactivate Environment

```bash
deactivate
```

### Update Dependencies

```bash
source venv/bin/activate
pip install --upgrade sounddevice numpy faster-whisper
```

## 📱 What the App Does

1. **Captures system audio** via BlackHole 2ch
2. **Converts speech to text** in real-time using Whisper AI
3. **Displays live subtitles** in an overlay window
4. **Works with any audio** playing on your Mac (videos, calls, music, etc.)

## 🆘 Troubleshooting

- **"BlackHole device not found"**: Install BlackHole 2ch and restart
- **"No audio captured"**: Check Multi-Output Device configuration
- **"ASR model error"**: Ensure virtual environment is activated

## 🎯 Ready to Go!

Once BlackHole 2ch is installed and audio is configured, you'll have a fully functional live subtitle system for your Mac!

---

**Current Status**: ✅ Python Environment Ready | ⚠️ BlackHole 2ch Needed
