#!/usr/bin/env python3
"""
Live Audio Monitor
Real-time audio level display for testing audio capture
"""

import sounddevice as sd
import numpy as np
import tkinter as tk
from tkinter import font as tkfont
import threading
import queue
import time

class LiveAudioMonitor:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Live Audio Monitor")
        self.root.geometry("400x300")
        self.root.configure(bg='black')
        
        # Audio settings
        self.sample_rate = 16000
        self.chunk_size = 1024
        self.audio_queue = queue.Queue()
        self.running = True
        
        # GUI elements
        self.setup_gui()
        
        # Start audio capture
        self.start_audio_capture()
        
    def setup_gui(self):
        """Setup the GUI elements"""
        # Title
        title_label = tk.Label(self.root, text="🎵 Live Audio Monitor", 
                              font=tkfont.Font(size=16, weight='bold'),
                              fg='lime', bg='black')
        title_label.pack(pady=10)
        
        # Audio level display
        self.level_var = tk.StringVar(value="Waiting for audio...")
        self.level_label = tk.Label(self.root, textvariable=self.level_var,
                                   font=tkfont.Font(size=14),
                                   fg='white', bg='black')
        self.level_label.pack(pady=5)
        
        # Visual level bar
        self.level_canvas = tk.Canvas(self.root, width=300, height=40, 
                                     bg='darkgray', highlightthickness=0)
        self.level_canvas.pack(pady=10)
        
        # Device info
        self.device_var = tk.StringVar(value="Device: Unknown")
        self.device_label = tk.Label(self.root, textvariable=self.device_var,
                                    font=tkfont.Font(size=10),
                                    fg='yellow', bg='black')
        self.device_label.pack(pady=5)
        
        # Instructions
        instructions = tk.Label(self.root, 
                              text="Speak or play audio to see levels\nPress Q to quit",
                              font=tkfont.Font(size=10),
                              fg='gray', bg='black')
        instructions.pack(pady=10)
        
        # Bind quit key
        self.root.bind('<KeyPress-q>', lambda e: self.quit_app())
        self.root.bind('<Escape>', lambda e: self.quit_app())
        
        # Update GUI
        self.update_gui()
        
    def start_audio_capture(self):
        """Start audio capture in a separate thread"""
        def audio_callback(indata, frames, time_info, status):
            if status:
                print(f"Audio status: {status}")
            # Calculate RMS level
            rms = np.sqrt(np.mean(indata**2))
            self.audio_queue.put(rms)
        
        def audio_thread():
            try:
                with sd.InputStream(samplerate=self.sample_rate, 
                                  channels=1, 
                                  callback=audio_callback,
                                  blocksize=self.chunk_size):
                    while self.running:
                        time.sleep(0.01)
            except Exception as e:
                print(f"Audio error: {e}")
        
        # Start audio thread
        self.audio_thread = threading.Thread(target=audio_thread, daemon=True)
        self.audio_thread.start()
        
        # Update device info
        try:
            devices = sd.query_devices()
            input_devices = [i for i, d in enumerate(devices) 
                           if d.get('max_input_channels', 0) > 0]
            if input_devices:
                device_info = sd.query_devices(input_devices[0])
                device_name = device_info.get('name', 'Unknown')
                self.device_var.set(f"Device: {device_name}")
        except Exception as e:
            print(f"Error getting device info: {e}")
    
    def update_gui(self):
        """Update the GUI with current audio levels"""
        try:
            while not self.audio_queue.empty():
                rms = self.audio_queue.get_nowait()
                
                # Convert to dB
                db = 20 * np.log10(max(rms, 1e-10))
                
                # Normalize to 0-100%
                level_percent = max(0, min(100, (db + 60) * 1.67))
                
                # Update level display
                self.level_var.set(f"Level: {level_percent:.1f}% ({db:.1f} dB)")
                
                # Update visual bar
                self.update_level_bar(level_percent)
                
        except queue.Empty:
            pass
        
        # Schedule next update
        if self.running:
            self.root.after(50, self.update_gui)
    
    def update_level_bar(self, level_percent):
        """Update the visual level bar"""
        self.level_canvas.delete("all")
        
        # Background
        self.level_canvas.create_rectangle(0, 0, 300, 40, 
                                         fill='darkgray', outline='white')
        
        # Level bar
        bar_width = int((level_percent / 100.0) * 300)
        
        # Color based on level
        if level_percent > 80:
            color = 'red'
        elif level_percent > 50:
            color = 'yellow'
        else:
            color = 'green'
        
        self.level_canvas.create_rectangle(0, 0, bar_width, 40, 
                                         fill=color, outline='')
        
        # Level text
        self.level_canvas.create_text(150, 20, 
                                     text=f"{level_percent:.1f}%",
                                     fill='black', 
                                     font=tkfont.Font(size=12, weight='bold'))
    
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
            print("Audio monitor stopped")

def main():
    print("Starting Live Audio Monitor...")
    print("Press Q or Esc to quit")
    
    app = LiveAudioMonitor()
    app.run()

if __name__ == "__main__":
    main() 