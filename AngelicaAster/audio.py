import numpy as np
import pyaudio
from collections import deque

sound = True
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100

DebugQueue = deque(maxlen=int(RATE / CHUNK * 5))

def flush(playback=True):
    p = pyaudio.PyAudio()
    InputStream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    input_device_index = 31,
                    frames_per_buffer=CHUNK)
    if playback:
        OutputStream = p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            output=True,
            output_device_index=5,
            frames_per_buffer=CHUNK
        )
    while True:
        try:
            data = InputStream.read(CHUNK)
            if playback:
                OutputStream.write(data)
        except Exception:
            break

def listen_fishing(playback=True):
    p = pyaudio.PyAudio()
    InputStream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    input_device_index = 31,
                    frames_per_buffer=CHUNK)
    if playback:
        OutputStream = p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            output=True,
            output_device_index=5,
            frames_per_buffer=CHUNK
        )
    try:
        while True:
            data = InputStream.read(CHUNK, exception_on_overflow=False)
            if playback:
                OutputStream.write(data)
            samples = np.frombuffer(data, dtype=np.int16)
            fft_values = np.fft.rfft(samples)
            magnitudes = np.abs(fft_values)
            DebugQueue.append(magnitudes[-5:])
            if magnitudes[-2] >= 60000:
                print([int(n) for n in magnitudes[-5:]])
                break
    finally:
        InputStream.stop_stream()
        InputStream.close()
        OutputStream.stop_stream()
        OutputStream.close()
        p.terminate()
    return True