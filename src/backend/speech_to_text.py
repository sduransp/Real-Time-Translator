import datetime
import logging
import os
import wave
import threading
import tempfile
import numpy as np
import sounddevice as sd
from openai import OpenAI
import whisper
import warnings

# Suprimir la advertencia de FP16
warnings.filterwarnings("ignore", message="FP16 is not supported on CPU; using FP32 instead")

class RealTimeTranscriber:
    def __init__(self, model_name="base", sample_rate=16000):
        self.sample_rate = sample_rate
        self.model = whisper.load_model(model_name)
        self.is_running = False
        self.queue = np.ndarray([], dtype=np.float32)
        self.mutex = threading.Lock()
        self.chunk_size = 1024
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        self.audio_interface = sd.InputStream(samplerate=self.sample_rate, channels=1, dtype="float32", callback=self.callback)

    def callback(self, indata, frames, time, status):
        with self.mutex:
            self.queue = np.append(self.queue, indata.ravel())
            if len(self.queue) >= self.chunk_size:
                audio_chunk = self.queue[:self.chunk_size]
                self.queue = self.queue[self.chunk_size:]
                self.transcribe(audio_chunk)

    def transcribe(self, audio_chunk):
        pcm_data = (audio_chunk * 32767).astype(np.int16).tobytes()
        with wave.open(self.temp_file.name, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(self.sample_rate)
            wf.writeframes(pcm_data)
        result = self.model.transcribe(self.temp_file.name, language='es')
        print(result['text'])

    def start(self):
        self.is_running = True
        with self.audio_interface as stream:
            while self.is_running:
                sd.sleep(1000)

    def stop(self):
        self.is_running = False
        self.audio_interface.abort()

if __name__ == "__main__":
    transcriber = RealTimeTranscriber()
    try:
        transcriber.start()
    except KeyboardInterrupt:
        transcriber.stop()
        os.unlink(transcriber.temp_file.name)
        print("Transcription stopped.")