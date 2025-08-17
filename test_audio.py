#!/usr/bin/env python3
"""
Simple Audio Capture Test
Tests if we can capture audio from available devices
"""

import sounddevice as sd
import numpy as np
import time

def list_audio_devices():
    """List all available audio devices"""
    print("Available Audio Devices:")
    print("=" * 50)
    
    devices = sd.query_devices()
    for i, device in enumerate(devices):
        name = device.get('name', 'Unknown')
        max_inputs = device.get('max_input_channels', 0)
        max_outputs = device.get('max_output_channels', 0)
        sample_rate = device.get('default_samplerate', 'Unknown')
        
        print(f"{i:2d}: {name}")
        print(f"     Inputs: {max_inputs}, Outputs: {max_outputs}, Sample Rate: {sample_rate}")
        print()

def test_audio_capture(device_id, duration=5):
    """Test audio capture from a specific device"""
    print(f"Testing audio capture from device {device_id} for {duration} seconds...")
    
    try:
        # Get device info
        device_info = sd.query_devices(device_id)
        print(f"Device: {device_info.get('name', 'Unknown')}")
        print(f"Sample Rate: {device_info.get('default_samplerate', 'Unknown')}")
        print(f"Channels: {device_info.get('max_input_channels', 'Unknown')}")
        
        # Capture audio
        audio_data = sd.rec(int(duration * 44100), samplerate=44100, channels=1, dtype='float32', device=device_id)
        print("Recording... Speak or play some audio...")
        
        sd.wait()  # Wait for recording to complete
        
        # Analyze the audio
        rms = np.sqrt(np.mean(audio_data**2))
        db = 20 * np.log10(max(rms, 1e-10))
        
        print(f"Audio captured successfully!")
        print(f"RMS Level: {rms:.6f}")
        print(f"dB Level: {db:.2f} dB")
        print(f"Audio shape: {audio_data.shape}")
        
        if rms > 0.001:  # Threshold for detecting actual audio
            print("✅ Audio detected - device is working!")
        else:
            print("⚠️  No significant audio detected - check if audio is playing")
            
    except Exception as e:
        print(f"❌ Error testing device {device_id}: {e}")

def main():
    print("Audio Capture Test")
    print("=" * 30)
    
    # List all devices
    list_audio_devices()
    
    # Test the first available input device
    devices = sd.query_devices()
    input_devices = []
    
    for i, device in enumerate(devices):
        if device.get('max_input_channels', 0) > 0:
            input_devices.append(i)
    
    if input_devices:
        print(f"Found {len(input_devices)} input devices")
        test_device = input_devices[0]
        print(f"Testing first input device: {test_device}")
        test_audio_capture(test_device)
    else:
        print("No input devices found!")
    
    print("\nTest complete!")

if __name__ == "__main__":
    main() 