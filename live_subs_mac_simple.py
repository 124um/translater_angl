#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
macOS Live Subtitles Overlay (Simplified Version)

- Захватывает системный звук через виртуальный девайс BlackHole 2ch
- Простая демонстрация без ASR (показывает аудио уровни)
- Tkinter overlay: безрамочное окно, всегда поверх
- Работает как тест аудио захвата

Зависимости:
  pip install sounddevice numpy
"""

import os
import sys
import time
import queue
import threading
import numpy as np
import sounddevice as sd
import tkinter as tk
from tkinter import font as tkfont

# ------------------ Конфиг ------------------
TARGET_SR = 16000               # частота для обработки
BLOCK_SEC = 0.1                 # длина блока для анализа
GUI_REFRESH_MS = 100            # ms между обновлениями GUI
FONT_FAMILY = "Helvetica"
FONT_SIZE = 18
WINDOW_OPACITY = 0.90           # 0..1

# Горячие клавиши:
#  [+]/[-] — увеличить/уменьшить шрифт
#  [,]/[.] — уменьшить/увеличить прозрачность
#  [C] — очистить экран
#  [Q]/[Esc] — выйти

# --------------------------------------------
# Аудио: поиск устройства BlackHole и поток
# --------------------------------------------
def pick_blackhole_device():
    """Возвращает индекс входного устройства 'BlackHole' (input=True)."""
    devices = sd.query_devices()
    candidates = []
    for i, d in enumerate(devices):
        name = str(d.get("name", "")).lower()
        max_in = int(d.get("max_input_channels", 0))
        if "blackhole" in name and max_in > 0:
            candidates.append(i)
    
    if candidates:
        return candidates[0]
    
    # Если не нашли — подскажем и покажем список
    print("[Audio] Не найден вход BlackHole. Доступные устройства:")
    for i, d in enumerate(devices):
        if d.get("max_input_channels", 0) > 0:
            print(f"  {i}: {d.get('name', 'Unknown')} (channels: {d.get('max_input_channels', 0)})")
    
    print("\n• Убедись, что установлен BlackHole 2ch")
    print("• В Audio MIDI Setup создай Multi-Output с BlackHole и выбери его в System Output.")
    print("\nПопробуем использовать первое доступное устройство...")
    
    # Попробуем первое устройство с входом
    for i, d in enumerate(devices):
        if d.get("max_input_channels", 0) > 0:
            print(f"[Audio] Используем устройство #{i}: {d.get('name', 'Unknown')}")
            return i
    
    print("[Audio] Нет доступных входных устройств!")
    sys.exit(2)

# Очереди/флаги
raw_q = queue.Queue()
audio_levels = queue.Queue()
terminate = threading.Event()

# --------------------------------------------
# Поток захвата аудио
# --------------------------------------------
def audio_callback(indata, frames, time_info, status):
    if status:
        print(f"[Audio] {status}", file=sys.stderr)
    raw_q.put(indata.copy())

def audio_thread():
    dev_index = pick_blackhole_device()
    dev_info = sd.query_devices(dev_index)
    src_sr = int(dev_info.get("default_samplerate", 48000))
    channels = min(2, int(dev_info.get("max_input_channels", 1))) or 1
    blocksize = int(src_sr * 0.05)  # 50мс блоки

    print(f"[Audio] Using device #{dev_index}: {dev_info['name']} @ {src_sr} Hz, ch={channels}")

    with sd.InputStream(device=dev_index,
                        channels=channels,
                        samplerate=src_sr,
                        blocksize=blocksize,
                        dtype="float32",
                        callback=audio_callback):
        while not terminate.is_set():
            time.sleep(0.05)

# --------------------------------------------
# Поток анализа аудио
# --------------------------------------------
def audio_analysis_thread():
    while not terminate.is_set():
        try:
            block = raw_q.get(timeout=0.1)
        except queue.Empty:
            continue

        if block.ndim == 2:
            mono = block.mean(axis=1)
        else:
            mono = block.astype(np.float32, copy=False)

        # Вычисляем RMS уровень
        rms = np.sqrt(np.mean(mono**2))
        # Конвертируем в dB
        db = 20 * np.log10(max(rms, 1e-10))
        
        # Нормализуем к 0-100%
        level = max(0, min(100, (db + 60) * 1.67))  # -60dB to 0dB -> 0-100%
        
        audio_levels.put(level)
        time.sleep(0.02)

# --------------------------------------------
# GUI (Tkinter overlay)
# --------------------------------------------
class OverlayApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Live Audio Monitor")
        self.root.overrideredirect(True)  # без рамки
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", WINDOW_OPACITY)

        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        w = int(sw * 0.60)
        h = int(sh * 0.15)
        x = int((sw - w) / 2)
        y = int(sh - h - 40)
        self.root.geometry(f"{w}x{h}+{x}+{y}")

        self.font_size = FONT_SIZE
        self.font = tkfont.Font(family=FONT_FAMILY, size=self.font_size)
        
        # Создаем фрейм для содержимого
        self.content_frame = tk.Frame(self.root, bg="#000000")
        self.content_frame.pack(fill="both", expand=True, padx=16, pady=12)
        
        # Заголовок
        self.title_label = tk.Label(self.content_frame, 
                                   text="🎵 Live Audio Monitor", 
                                   font=tkfont.Font(family=FONT_FAMILY, size=self.font_size-2),
                                   fg="#00FF00", bg="#000000")
        self.title_label.pack(pady=(0, 8))
        
        # Уровень аудио
        self.level_var = tk.StringVar(value="Waiting for audio...")
        self.level_label = tk.Label(self.content_frame, 
                                   textvariable=self.level_var,
                                   font=self.font, 
                                   fg="#FFFFFF", bg="#000000")
        self.level_label.pack(pady=4)
        
        # Прогресс бар
        self.progress = tk.Canvas(self.content_frame, 
                                 height=20, 
                                 bg="#333333", 
                                 highlightthickness=0)
        self.progress.pack(fill="x", pady=8)
        
        # Инструкции
        self.help_var = tk.StringVar(value="Controls: +/- font, [] opacity, C clear, Q quit")
        self.help_label = tk.Label(self.content_frame, 
                                  textvariable=self.help_var,
                                  font=tkfont.Font(family=FONT_FAMILY, size=self.font_size-4),
                                  fg="#888888", bg="#000000")
        self.help_label.pack(pady=(8, 0))

        self._drag_data = {"x": 0, "y": 0}
        self.content_frame.bind("<ButtonPress-1>", self._start_move)
        self.content_frame.bind("<B1-Motion>", self._on_move)

        self.root.bind("<KeyPress-plus>", self._inc_font)
        self.root.bind("<KeyPress-equal>", self._inc_font)
        self.root.bind("<KeyPress-minus>", self._dec_font)
        self.root.bind("<KeyPress-bracketleft>", self._dec_alpha)
        self.root.bind("<KeyPress-bracketright>", self._inc_alpha)
        self.root.bind("<KeyPress-c>", self._clear)
        self.root.bind("<Escape>", self._quit)
        self.root.bind("<KeyPress-q>", self._quit)

        self.root.after(GUI_REFRESH_MS, self._tick)

    def _start_move(self, event):
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

    def _on_move(self, event):
        x = self.root.winfo_x() + event.x - self._drag_data["x"]
        y = self.root.winfo_y() + event.y - self._drag_data["y"]
        self.root.geometry(f"+{x}+{y}")

    def _inc_font(self, event=None):
        self.font_size += 2
        self.font.configure(size=self.font_size)
        self.title_label.configure(font=tkfont.Font(family=FONT_FAMILY, size=self.font_size-2))

    def _dec_font(self, event=None):
        self.font_size = max(10, self.font_size - 2)
        self.font.configure(size=self.font_size)
        self.title_label.configure(font=tkfont.Font(family=FONT_FAMILY, size=self.font_size-2))

    def _inc_alpha(self, event=None):
        a = float(self.root.attributes("-alpha"))
        a = min(1.0, a + 0.05)
        self.root.attributes("-alpha", a)

    def _dec_alpha(self, event=None):
        a = float(self.root.attributes("-alpha"))
        a = max(0.3, a - 0.05)
        self.root.attributes("-alpha", a)

    def _clear(self, event=None):
        self.level_var.set("Cleared")

    def _quit(self, event=None):
        terminate.set()
        self.root.destroy()

    def _update_progress_bar(self, level):
        # Очищаем и перерисовываем прогресс бар
        self.progress.delete("all")
        
        # Фон
        self.progress.create_rectangle(0, 0, self.progress.winfo_width(), 20, 
                                     fill="#333333", outline="")
        
        # Прогресс
        width = self.progress.winfo_width()
        progress_width = int((level / 100.0) * width)
        
        if level > 80:
            color = "#FF0000"  # Красный для высоких уровней
        elif level > 50:
            color = "#FFFF00"  # Желтый для средних
        else:
            color = "#00FF00"  # Зеленый для низких
            
        self.progress.create_rectangle(0, 0, progress_width, 20, 
                                     fill=color, outline="")
        
        # Текст уровня
        self.progress.create_text(width//2, 10, 
                                text=f"{level:.1f}%", 
                                fill="#FFFFFF", 
                                font=tkfont.Font(family=FONT_FAMILY, size=10))

    def _tick(self):
        try:
            while True:
                level = audio_levels.get_nowait()
                self.level_var.set(f"Audio Level: {level:.1f}%")
                self._update_progress_bar(level)
        except queue.Empty:
            pass

        self.root.after(GUI_REFRESH_MS, self._tick)

    def run(self):
        self.root.mainloop()

# --------------------------------------------
# main
# --------------------------------------------
def main():
    print("[Init] Запуск упрощенной версии Live Audio Monitor...")
    print("[Init] Эта версия показывает уровни аудио без ASR")

    print("[Init] Запуск аудиопотока…")
    t_audio = threading.Thread(target=audio_thread, daemon=True)
    t_audio.start()

    print("[Init] Запуск анализа аудио…")
    t_analysis = threading.Thread(target=audio_analysis_thread, daemon=True)
    t_analysis.start()

    print("[Init] Запуск оверлей-окна… (горячие клавиши: +/- шрифт, [] прозрачность, C очистка, Q/Esc выход)")
    app = OverlayApp()
    try:
        app.run()
    finally:
        terminate.set()
        t_audio.join(timeout=1.0)
        t_analysis.join(timeout=1.0)
        print("[Exit] Bye.")

if __name__ == "__main__":
    main() 