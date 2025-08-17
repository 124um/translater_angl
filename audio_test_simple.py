#!/usr/bin/env python3
"""
Simple Audio Test - Shows what's happening with audio capture
"""

import sounddevice as sd
import numpy as np
import time

def test_audio_capture():
    """Test audio capture and explain the issue"""
    print("🔍 Audio Capture Test")
    print("=" * 50)
    
    # List all devices
    devices = sd.query_devices()
    print("\n📱 Available Audio Devices:")
    for i, device in enumerate(devices):
        name = device.get('name', 'Unknown')
        inputs = device.get('max_input_channels', 0)
        outputs = device.get('max_output_channels', 0)
        print(f"  {i}: {name}")
        print(f"      Inputs: {inputs}, Outputs: {outputs}")
        if "blackhole" in name.lower():
            print(f"      ⭐ BLACKHOLE DEVICE FOUND!")
        print()
    
    # Find input devices
    input_devices = []
    for i, device in enumerate(devices):
        if device.get('max_input_channels', 0) > 0:
            input_devices.append(i)
    
    if not input_devices:
        print("❌ No input devices found!")
        return
    
    print(f"🎤 Found {len(input_devices)} input device(s): {input_devices}")
    
    # Test first input device
    device_id = input_devices[0]
    device_info = sd.query_devices(device_id)
    device_name = device_info.get('name', 'Unknown')
    
    print(f"\n🎯 Testing device #{device_id}: {device_name}")
    print("📝 This will capture from your MICROPHONE, not system audio")
    print("🎬 To capture VIDEO audio, you need BlackHole 2ch installed")
    
    # Test capture
    print(f"\n🎤 Recording 5 seconds from {device_name}...")
    print("💡 Speak into your microphone to test...")
    
    try:
        # Record audio
        audio_data = sd.rec(int(5 * 16000), samplerate=16000, channels=1, dtype='float32', device=device_id)
        sd.wait()
        
        # Analyze
        rms = np.sqrt(np.mean(audio_data**2))
        db = 20 * np.log10(max(rms, 1e-10))
        
        print(f"\n📊 Results:")
        print(f"  Audio captured: {len(audio_data)} samples")
        print(f"  RMS Level: {rms:.6f}")
        print(f"  dB Level: {db:.2f} dB")
        
        if rms > 0.001:
            print("  ✅ Audio detected from microphone")
        else:
            print("  ⚠️  No significant audio detected")
            
        print(f"\n🔍 What this means:")
        print(f"  • Device #{device_id} ({device_name}) is working")
        print(f"  • It can capture MICROPHONE audio")
        print(f"  • It CANNOT capture SYSTEM AUDIO (videos, music)")
        print(f"  • For system audio, you need BlackHole 2ch")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def explain_solution():
    """Explain how to get system audio working"""
    print("\n" + "=" * 60)
    print("🔧 SOLUTION: How to Capture System Audio")
    print("=" * 60)
    
    print("\n🎯 Current Problem:")
    print("  • Your app only captures from microphone")
    print("  • Videos, music, and system sounds are not captured")
    print("  • MacBook Pro Speakers is OUTPUT only (no inputs)")
    
    print("\n✅ Solution: Install BlackHole 2ch")
    print("  1. Download from: https://existential.audio/blackhole/")
    print("  2. Install the .pkg file")
    print("  3. Restart your Mac")
    print("  4. Configure Audio MIDI Setup:")
    print("     • Create Multi-Output Device")
    print("     • Include BlackHole 2ch + your speakers")
    print("     • Set as System Output")
    
    print("\n🎬 After BlackHole installation:")
    print("  • App will detect BlackHole device")
    print("  • Can capture system audio (videos, music)")
    print("  • Will show real subtitles from video content")
    
    print("\n💡 Alternative for now:")
    print("  • Speak into microphone to test the app")
    print("  • App will show demo subtitles when you speak")
    print("  • This confirms the basic functionality works")

def main():
    test_audio_capture()
    explain_solution()
    
    print("\n🎯 Next Steps:")
    print("  1. Test microphone capture (speak into mic)")
    print("  2. Install BlackHole 2ch for system audio")
    print("  3. Configure audio routing")
    print("  4. Enjoy live subtitles from videos!")

if __name__ == "__main__":
    main() 