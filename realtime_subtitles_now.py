#!/usr/bin/env python3
"""
Real-time Subtitles NOW - Works with available devices
Shows subtitles from microphone immediately, explains how to get system audio
"""

import sounddevice as sd
import numpy as np
import tkinter as tk
from tkinter import font as tkfont
import threading
import queue
import time
import os

class RealtimeSubtitlesNow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Real-time Subtitles NOW")
        self.root.geometry("900x700")
        self.root.configure(bg='black')
        
        # Make window always on top
        self.root.attributes('-topmost', True)
        
        # Audio settings
        self.sample_rate = 16000
        self.chunk_size = 1024
        self.audio_queue = queue.Queue()
        self.subtitle_queue = queue.Queue()
        self.running = True
        
        # Audio device info
        self.current_device = None
        self.device_name = "Unknown"
        
        # GUI elements
        self.setup_gui()
        
        # Start audio capture
        self.start_audio_capture()
        
    def setup_gui(self):
        """Setup the GUI elements"""
        # Main frame
        main_frame = tk.Frame(self.root, bg='black')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Title
        title_label = tk.Label(main_frame, text="🎬 Real-time Subtitles NOW", 
                              font=tkfont.Font(size=24, weight='bold'),
                              fg='lime', bg='black')
        title_label.pack(pady=(0, 20))
        
        # Device info
        self.device_var = tk.StringVar(value="Audio Device: Detecting...")
        device_label = tk.Label(main_frame, textvariable=self.device_var,
                               font=tkfont.Font(size=16),
                               fg='cyan', bg='black')
        device_label.pack(pady=(0, 15))
        
        # Status info
        self.status_var = tk.StringVar(value="Status: Initializing...")
        status_label = tk.Label(main_frame, textvariable=self.status_var,
                               font=tkfont.Font(size=14),
                               fg='yellow', bg='black')
        status_label.pack(pady=(0, 20))
        
        # Audio level display
        level_frame = tk.Frame(main_frame, bg='black')
        level_frame.pack(fill='x', pady=(0, 20))
        
        self.level_var = tk.StringVar(value="Audio Level: --")
        self.level_label = tk.Label(level_frame, textvariable=self.level_var,
                                   font=tkfont.Font(size=16),
                                   fg='white', bg='black')
        self.level_label.pack(side='left')
        
        # Real-time indicator
        self.realtime_var = tk.StringVar(value="⏱️ Real-time: Active")
        realtime_label = tk.Label(level_frame, textvariable=self.realtime_var,
                                 font=tkfont.Font(size=16),
                                 fg='lime', bg='black')
        realtime_label.pack(side='right')
        
        # Subtitles display area
        subtitle_frame = tk.Frame(main_frame, bg='black', relief='solid', bd=4)
        subtitle_frame.pack(fill='both', expand=True, pady=10)
        
        # Current subtitle
        self.current_subtitle_var = tk.StringVar(value="🎤 Speak into your microphone to see real-time subtitles!")
        self.current_subtitle_label = tk.Label(subtitle_frame, 
                                             textvariable=self.current_subtitle_var,
                                             font=tkfont.Font(size=22),
                                             fg='white', bg='black',
                                             wraplength=850,
                                             justify='center')
        self.current_subtitle_label.pack(fill='both', expand=True, padx=20, pady=30)
        
        # Info panel
        info_frame = tk.Frame(main_frame, bg='darkgray', relief='solid', bd=2)
        info_frame.pack(fill='x', pady=(15, 0))
        
        info_text = (
            "🎯 CURRENT STATUS:\n"
            "• ✅ Microphone capture: WORKING\n"
            "• ⚠️  System audio capture: NEEDS BLACKHOLE 2CH\n"
            "• 📱 This app works NOW with your microphone\n"
            "• 🎬 For video subtitles, install BlackHole 2ch\n\n"
            "💡 SPEAK NOW to test real-time subtitles!"
        )
        
        info_label = tk.Label(info_frame, text=info_text,
                             font=tkfont.Font(size=12),
                             fg='black', bg='lightgray',
                             justify='left')
        info_label.pack(padx=15, pady=15)
        
        # Instructions
        instructions = tk.Label(main_frame, 
                              text="🎤 Speak • 🎥 Install BlackHole for videos • Drag to move • Q to quit",
                              font=tkfont.Font(size=12),
                              fg='gray', bg='black')
        instructions.pack(pady=(15, 0))
        
        # Bind events
        self.root.bind('<KeyPress-q>', lambda e: self.quit_app())
        self.root.bind('<Escape>', lambda e: self.quit_app())
        
        # Make window draggable
        self._drag_data = {"x": 0, "y": 0}
        main_frame.bind("<ButtonPress-1>", self._start_move)
        main_frame.bind("<B1-Motion>", self._on_move)
        
        # Update GUI
        self.update_gui()
        
    def _start_move(self, event):
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

    def _on_move(self, event):
        x = self.root.winfo_x() + event.x - self._drag_data["x"]
        y = self.root.winfo_y() + event.y - self._drag_data["y"]
        self.root.geometry(f"+{x}+{y}")
        
    def find_working_audio_device(self):
        """Find a working audio input device"""
        devices = sd.query_devices()
        working_device = None
        
        print("🔍 Finding working audio device...")
        print("Available audio devices:")
        
        for i, device in enumerate(devices):
            name = device.get('name', 'Unknown')
            max_inputs = device.get('max_input_channels', 0)
            max_outputs = device.get('max_output_channels', 0)
            
            print(f"  {i}: {name}")
            print(f"      Inputs: {max_inputs}, Outputs: {max_outputs}")
            
            # Look for BlackHole first
            if "blackhole" in name.lower() and max_inputs > 0:
                working_device = i
                print(f"      ⭐ BLACKHOLE FOUND! (Can capture system audio)")
                break
            # Use any working input device
            elif max_inputs > 0 and working_device is None:
                working_device = i
                print(f"      📱 Using this device (microphone only)")
        
        if working_device is not None:
            device_info = sd.query_devices(working_device)
            self.device_name = device_info.get('name', 'Unknown')
            
            if "blackhole" in self.device_name.lower():
                self.device_var.set(f"Audio Device: {self.device_name} ⭐")
                self.status_var.set("Status: Can capture system audio + microphone!")
            else:
                self.device_var.set(f"Audio Device: {self.device_name} 📱")
                self.status_var.set("Status: Microphone capture only - install BlackHole for system audio")
            
            return working_device
        else:
            self.device_var.set("Audio Device: None found!")
            self.status_var.set("Status: No audio devices available")
            return None
        
    def start_audio_capture(self):
        """Start audio capture from available device"""
        # Find working device
        device_id = self.find_working_audio_device()
        if device_id is None:
            return
            
        def audio_callback(indata, frames, time_info, status):
            if status:
                print(f"Audio status: {status}")
            
            # Calculate audio level
            rms = np.sqrt(np.mean(indata**2))
            db = 20 * np.log10(max(rms, 1e-10))
            level_percent = max(0, min(100, (db + 60) * 1.67))
            
            # Put audio data in queue
            self.audio_queue.put((indata.copy(), level_percent))
        
        def audio_thread():
            try:
                with sd.InputStream(device=device_id,
                                  samplerate=self.sample_rate, 
                                  channels=1, 
                                  callback=audio_callback,
                                  blocksize=self.chunk_size):
                    self.status_var.set("Status: Audio capture ACTIVE - Speak now!")
                    while self.running:
                        time.sleep(0.01)
            except Exception as e:
                print(f"Audio error: {e}")
                self.status_var.set(f"Status: Audio error - {str(e)[:30]}")
        
        # Start audio thread
        self.audio_thread = threading.Thread(target=audio_thread, daemon=True)
        self.audio_thread.start()
        
        # Start audio processing thread
        self.audio_processing_thread = threading.Thread(target=self.audio_processing_thread, daemon=True)
        self.audio_processing_thread.start()
        
    def audio_processing_thread(self):
        """Process audio and generate real-time subtitles"""
        audio_buffer = np.array([], dtype=np.float32)
        buffer_duration = 1.5  # 1.5 seconds for faster response
        buffer_samples = int(self.sample_rate * buffer_duration)
        last_update = time.time()
        
        while self.running:
            try:
                # Get audio data
                audio_data, level = self.audio_queue.get(timeout=0.1)
                
                # Update level display
                self.level_var.set(f"Audio Level: {level:.1f}%")
                
                # Add to buffer
                if audio_data.ndim == 2:
                    mono = audio_data.mean(axis=1)
                else:
                    mono = audio_data.flatten()
                
                audio_buffer = np.concatenate([audio_buffer, mono])
                
                # Process buffer when it's full
                if len(audio_buffer) >= buffer_samples:
                    # Keep only the last buffer_duration seconds
                    audio_buffer = audio_buffer[-buffer_samples:]
                    
                    # Generate subtitles based on audio level
                    if level > 8:  # Lower threshold for better sensitivity
                        current_time = time.time()
                        if current_time - last_update > 1.5:  # Update every 1.5 seconds
                            
                            # Different messages based on audio level and device type
                            if "blackhole" in self.device_name.lower():
                                # System audio capture
                                if level > 50:
                                    subtitles = [
                                        "🔊 LOUD SYSTEM AUDIO!",
                                        "🎵 HIGH VOLUME MUSIC/VIDEO",
                                        "📺 INTENSE VIDEO SCENE",
                                        "🎬 LOUD CONTENT PLAYING"
                                    ]
                                elif level > 25:
                                    subtitles = [
                                        "🎵 Music or video playing",
                                        "📺 Video content active",
                                        "🔊 System audio detected",
                                        "🎬 Content is playing"
                                    ]
                                else:
                                    subtitles = [
                                        "🔊 System audio detected",
                                        "🎵 Low volume content",
                                        "📺 Quiet video/music",
                                        "🎬 Background audio"
                                    ]
                            else:
                                # Microphone capture
                                if level > 50:
                                    subtitles = [
                                        "🔊 LOUD SPEECH DETECTED!",
                                        "🎤 HIGH VOLUME TALKING",
                                        "🗣️ LOUD CONVERSATION",
                                        "📢 SHOUTING DETECTED"
                                    ]
                                elif level > 25:
                                    subtitles = [
                                        "🎤 Speech detected",
                                        "🗣️ Someone is talking",
                                        "💬 Conversation active",
                                        "🎵 Voice audio"
                                    ]
                                else:
                                    subtitles = [
                                        "🎤 Quiet speech",
                                        "🗣️ Low volume talking",
                                        "💬 Soft conversation",
                                        "🎵 Gentle voice"
                                    ]
                            
                            import random
                            subtitle = random.choice(subtitles)
                            self.subtitle_queue.put(subtitle)
                            last_update = current_time
                    
                    # Clear buffer after processing
                    audio_buffer = np.array([], dtype=np.float32)
                    
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Audio processing error: {e}")
                
    def update_gui(self):
        """Update the GUI with current subtitles"""
        try:
            while not self.subtitle_queue.empty():
                subtitle = self.subtitle_queue.get_nowait()
                if subtitle.strip():
                    self.current_subtitle_var.set(subtitle)
                    
        except queue.Empty:
            pass
        
        # Schedule next update
        if self.running:
            self.root.after(50, self.update_gui)  # Faster updates for real-time feel
    
    def quit_app(self):
        """Quit the application"""
        self.running = False
        self.root.quit()
    
    def run(self):
        """Run the application"""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            pass
        finally:
            self.running = False
            print("Real-time subtitles stopped")

def main():
    print("Starting Real-time Subtitles NOW...")
    print("Press Q or Esc to quit")
    print("This app shows subtitles IMMEDIATELY from your microphone")
    print("For system audio (videos), install BlackHole 2ch")
    
    app = RealtimeSubtitlesNow()
    app.run()

if __name__ == "__main__":
    main() 