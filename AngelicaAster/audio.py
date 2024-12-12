import numpy as np
import pyaudio

sound = True
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100

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
            if magnitudes[-2] > 16000:
                print([int(n) for n in magnitudes[-5:]])
                break
    finally:
        InputStream.stop_stream()
        InputStream.close()
        OutputStream.stop_stream()
        OutputStream.close()
        p.terminate()
    return True