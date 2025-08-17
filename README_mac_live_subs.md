# macOS Live Subtitles Overlay

This project captures **system audio** on macOS via **BlackHole 2ch** and displays **live English subtitles** in a **Tkinter overlay** window.

## 1) Install prerequisites
```bash
# Install Homebrew if needed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Virtual audio device
brew install blackhole-2ch

# Python deps
pip install sounddevice numpy faster-whisper
# optional fallback:
pip install openai-whisper torch
```

## 2) Configure Audio
1. Open **Audio MIDI Setup** → click **+** → **Create Multi-Output Device**.  
2. Check **BlackHole 2ch** and your real speakers/headphones.  
3. In **System Settings → Sound → Output**, select your **Multi-Output Device**.  
   (So you can hear audio and mirror it into BlackHole for capture.)

## 3) Run
```bash
python live_subs_mac.py
```
- A borderless overlay window will appear near the bottom of the screen.
- Hotkeys: `+/-` font size, `[`/`]` opacity, `C` clear, `Esc/Q` quit.

## Notes
- Model forced to English (`language="en"`). For autodetect, use a non-`.en` model and remove the `language` argument.
- For fullscreen apps that steal focus, a native Cocoa overlay (PyObjC) can be provided.
- To save `.srt` concurrently, we can extend the script with timing and a file writer.
