#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
macOS Live Subtitles Overlay (System Audio via BlackHole)

- Захватывает системный звук через виртуальный девайс BlackHole 2ch
  (системный Output должен быть настроен на Multi-Output Device с BlackHole).
- Реалтайм ASR: faster-whisper (предпочтительно) → fallback на openai-whisper.
- Tkinter overlay: безрамочное окно, всегда поверх, регулируемый шрифт/прозрачность,
  авто-перенос строк, удержание последних N строк.
- Работает на CPU; на Apple Silicon быстрее с faster-whisper.

Зависиомсти:
  pip install sounddevice numpy faster-whisper
  # опционально:
  pip install openai-whisper torch
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
TARGET_SR = 16000               # частота для ASR
BLOCK_SEC = 2.5                 # длина блока для распознавания
OVERLAP_SEC = 0.5               # перекрытие блоков
KEEP_LINES = 4                  # сколько строк держать на экране
GUI_REFRESH_MS = 150            # ms между обновлениями GUI
FONT_FAMILY = "Helvetica"
FONT_SIZE = 22
WINDOW_OPACITY = 0.90           # 0..1

ASR_MODEL = os.environ.get("ASR_MODEL", "small.en")  # "tiny", "base", "small.en", "medium"

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
    print(sd.query_devices())
    print("\n• Убедись, что установлен BlackHole 2ch (brew install blackhole-2ch)")
    print("• В Audio MIDI Setup создай Multi-Output с BlackHole и выбери его в System Output.")
    sys.exit(2)

def simple_resample(x, src_sr, dst_sr):
    """Лёгкий ресемплер (линейная интерполяция) без внешних зависимостей.
       x: float32 mono, shape (N,)"""
    if src_sr == dst_sr or len(x) == 0:
        return x.astype(np.float32, copy=False)
    ratio = dst_sr / float(src_sr)
    dst_len = int(round(len(x) * ratio))
    if dst_len <= 1:
        return x[:1].astype(np.float32, copy=False)
    xp = np.linspace(0, 1, num=len(x), dtype=np.float64)
    fp = x.astype(np.float64, copy=False)
    x_new = np.linspace(0, 1, num=dst_len, dtype=np.float64)
    y_new = np.interp(x_new, xp, fp).astype(np.float32)
    return y_new

# Очереди/флаги
raw_q = queue.Queue()
text_q = queue.Queue()
terminate = threading.Event()

# --------------------------------------------
# ASR: faster-whisper (приоритет) → whisper
# --------------------------------------------
ASR_BACKEND = None
asr_model = None

def cuda_available():
    try:
        import torch
        return bool(getattr(torch, "cuda", None)) and torch.cuda.is_available()
    except Exception:
        return False

def init_asr():
    global ASR_BACKEND, asr_model
    # Пытаемся faster-whisper
    try:
        from faster_whisper import WhisperModel  # type: ignore
        device = "cpu"  # на Mac обычно CPU
        compute_type = "int8"  # экономно по памяти
        asr_model = WhisperModel(ASR_MODEL, device=device, compute_type=compute_type)
        ASR_BACKEND = "faster"
        print(f"[ASR] faster-whisper: {ASR_MODEL}, device={device}, compute={compute_type}")
        return
    except Exception as e:
        print(f"[ASR] faster-whisper недоступен: {e}")

    # Фоллбек — openai-whisper
    try:
        import whisper  # type: ignore
        import torch
        device = "cuda" if cuda_available() else "cpu"
        asr_model = whisper.load_model(ASR_MODEL, device=device)
        ASR_BACKEND = "whisper"
        print(f"[ASR] whisper: {ASR_MODEL}, device={device}")
        return
    except Exception as e:
        print("[ASR] Нет доступной модели. Установи один из вариантов:")
        print("  pip install faster-whisper")
        print("  или pip install openai-whisper torch")
        print(f"  Ошибка: {e}")
        sys.exit(1)

def asr_transcribe_chunk(mono16k: np.ndarray) -> str:
    """mono16k: float32, 16000 Гц"""
    if ASR_BACKEND == "faster":
        from faster_whisper import WhisperModel  # type: ignore
        segments, info = asr_model.transcribe(
            mono16k,
            language="en",      # принудительно английские субтитры
            vad_filter=True,
            beam_size=1,
            temperature=0.0,
        )
        parts = []
        for seg in segments:
            t = (seg.text or "").strip()
            if t:
                parts.append(t)
        return " ".join(parts).strip()
    elif ASR_BACKEND == "whisper":
        import whisper  # type: ignore
        result = asr_model.transcribe(
            mono16k,
            language="en",      # фиксируем английский
            fp16=False,
            temperature=0.0,
            no_speech_threshold=0.1,
            condition_on_previous_text=False,
        )
        return (result.get("text") or "").strip()
    return ""

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
    src_sr = int(dev_info["default_samplerate"])
    channels = min(2, int(dev_info["max_input_channels"])) or 1
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
# Поток ASR
# --------------------------------------------
def asr_thread():
    src_buffer = np.zeros(0, dtype=np.float32)

    target_block = int(TARGET_SR * BLOCK_SEC)
    target_overlap = int(TARGET_SR * OVERLAP_SEC)

    approx_src_sr = 48000  # типично для BlackHole

    while not terminate.is_set():
        try:
            block = raw_q.get(timeout=0.1)
        except queue.Empty:
            continue

        if block.ndim == 2:
            mono = block.mean(axis=1)
        else:
            mono = block.astype(np.float32, copy=False)

        src_buffer = np.concatenate([src_buffer, mono])

        # ограничиваем буфер секундой на 60 при 48кГц
        if len(src_buffer) > 48000 * 60:
            src_buffer = src_buffer[-48000*60:]

        need_src_len = int((BLOCK_SEC + OVERLAP_SEC) * approx_src_sr)
        if len(src_buffer) >= need_src_len:
            src_chunk = src_buffer[-need_src_len:]
            mono16k = simple_resample(src_chunk, approx_src_sr, TARGET_SR)
            if len(mono16k) >= target_block:
                mono16k = mono16k[-target_block:]
            text = asr_transcribe_chunk(mono16k)
            if text:
                text_q.put(text)

        time.sleep(0.02)

# --------------------------------------------
# GUI (Tkinter overlay)
# --------------------------------------------
class OverlayApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Live Captions")
        self.root.overrideredirect(True)  # без рамки
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", WINDOW_OPACITY)

        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        w = int(sw * 0.70)
        h = int(sh * 0.18)
        x = int((sw - w) / 2)
        y = int(sh - h - 40)
        self.root.geometry(f"{w}x{h}+{x}+{y}")

        self.font_size = FONT_SIZE
        self.font = tkfont.Font(family=FONT_FAMILY, size=self.font_size)
        self.text_var = tk.StringVar(value="…waiting audio…")
        self.label = tk.Label(self.root, textvariable=self.text_var,
                              font=self.font, fg="#FFFFFF", bg="#000000",
                              wraplength=w-40, justify="center")
        self.label.pack(fill="both", expand=True, padx=16, pady=12)

        self._drag_data = {"x": 0, "y": 0}
        self.label.bind("<ButtonPress-1>", self._start_move)
        self.label.bind("<B1-Motion>", self._on_move)

        self.root.bind("<KeyPress-plus>", self._inc_font)
        self.root.bind("<KeyPress-equal>", self._inc_font)
        self.root.bind("<KeyPress-minus>", self._dec_font)
        self.root.bind("<KeyPress-bracketleft>", self._dec_alpha)
        self.root.bind("<KeyPress-bracketright>", self._inc_alpha)
        self.root.bind("<KeyPress-c>", self._clear)
        self.root.bind("<Escape>", self._quit)
        self.root.bind("<KeyPress-q>", self._quit)

        self.lines = []

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

    def _dec_font(self, event=None):
        self.font_size = max(10, self.font_size - 2)
        self.font.configure(size=self.font_size)

    def _inc_alpha(self, event=None):
        a = float(self.root.attributes("-alpha"))
        a = min(1.0, a + 0.05)
        self.root.attributes("-alpha", a)

    def _dec_alpha(self, event=None):
        a = float(self.root.attributes("-alpha"))
        a = max(0.3, a - 0.05)
        self.root.attributes("-alpha", a)

    def _clear(self, event=None):
        self.lines = []
        self.text_var.set("")

    def _quit(self, event=None):
        terminate.set()
        self.root.destroy()

    def _tick(self):
        try:
            while True:
                t = text_q.get_nowait()
                if t.strip():
                    self.lines.append(t.strip())
                    if len(self.lines) > KEEP_LINES:
                        self.lines = self.lines[-KEEP_LINES:]
        except queue.Empty:
            pass

        self.text_var.set("\n".join(self.lines))
        self.root.after(GUI_REFRESH_MS, self._tick)

    def run(self):
        self.root.mainloop()

# --------------------------------------------
# main
# --------------------------------------------
def main():
    print("[Init] Инициализация ASR…")
    init_asr()

    print("[Init] Запуск аудиопотока…")
    t_audio = threading.Thread(target=audio_thread, daemon=True)
    t_audio.start()

    print("[Init] Запуск ASR потока…")
    t_asr = threading.Thread(target=asr_thread, daemon=True)
    t_asr.start()

    print("[Init] Запуск оверлей-окна… (горячие клавиши: +/- шрифт, [] прозрачность, C очистка, Q/Esc выход)")
    app = OverlayApp()
    try:
        app.run()
    finally:
        terminate.set()
        t_audio.join(timeout=1.0)
        t_asr.join(timeout=1.0)
        print("[Exit] Bye.")

if __name__ == "__main__":
    main()
