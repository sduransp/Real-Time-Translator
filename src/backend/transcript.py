import os
import numpy as np
import speech_recognition as sr
import whisper
import torch
from queue import Queue
from datetime import datetime, timedelta
from time import sleep
from sys import platform
import pyaudio
from translation import text_transcript


class RealTimeSpeakerTranslator:
    """
    RealTimeSpeakerTranslator handles real-time speech recognition from speakers,
    translation to Spanish, and prints the text on the screen.

    Attributes:
        model_name (str): Whisper model to be used.
        energy_threshold (int): Energy threshold for speech recognition.
        record_timeout (int): Timeout duration for recording.
        phrase_timeout (int): Timeout duration for detecting phrase end.
        speaker_device_name (str): Speaker device name for audio input.
        phrase_time (datetime): Time of the last detected phrase.
        data_queue (Queue): Queue to store audio data.
        transcription (list): List to store transcriptions.
        recorder (Recognizer): Speech recognition instance.
        source (Microphone): Microphone instance for audio input.
        audio_model (WhisperModel): Whisper model for speech-to-text.
        p (PyAudio): PyAudio instance for handling audio input.
    """

    def __init__(self, model="tiny", energy_threshold=1000, record_timeout=3, phrase_timeout=3, speaker_device=1):
        """
        Initializes the RealTimeSpeakerTranslator with the given parameters.
        """
        self.model_name = model
        self.energy_threshold = energy_threshold
        self.record_timeout = record_timeout
        self.phrase_timeout = phrase_timeout
        self.speaker_device_name = 'Speakers (Realtek(R) Audio)'  # Change to your speaker device name
        
        self.phrase_time = None
        self.data_queue = Queue()
        self.transcription = ['']

        self.recorder = sr.Recognizer()
        self.recorder.energy_threshold = energy_threshold
        self.recorder.dynamic_energy_threshold = False
        
        self.setup_speaker()
        self.load_audio_model()

        self.p = pyaudio.PyAudio()

    def setup_speaker(self):
        """
        Sets up the speaker for audio input.
        """
        if 'linux' in platform:
            mic_name = self.speaker_device_name
            for index, name in enumerate(sr.Microphone.list_microphone_names()):
                if mic_name in name:
                    self.source = sr.Microphone(sample_rate=16000, device_index=index)
                    break
        else:
            self.source = sr.Microphone(sample_rate=16000)

    def load_audio_model(self):
        """
        Loads the Whisper audio model.
        """
        if self.model_name != "large":
            self.model_name += ".en"
        self.audio_model = whisper.load_model(self.model_name)

    def record_callback(self, _, audio: sr.AudioData) -> None:
        """
        Callback function to handle audio data.
        
        Args:
            audio (AudioData): The audio data.
        """
        data = audio.get_raw_data()
        self.data_queue.put(data)

    def start_listening(self):
        """
        Starts listening for audio input from the speaker.
        """
        with self.source:
            self.recorder.adjust_for_ambient_noise(self.source)
        self.recorder.listen_in_background(self.source, self.record_callback, phrase_time_limit=self.record_timeout)
        print("Model loaded.\n")

    def process_audio(self, audio_data):
        """
        Processes audio data to text using Whisper model.
        
        Args:
            audio_data (bytes): The audio data.
            
        Returns:
            str: Transcribed text.
        """
        audio_np = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
        result = self.audio_model.transcribe(audio_np, fp16=torch.cuda.is_available())
        return result['text'].strip()

    def run(self):
        """
        Runs the real-time translator.
        """
        self.start_listening()

        while True:
            try:
                now = datetime.utcnow()
                if not self.data_queue.empty():
                    phrase_complete = False
                    if self.phrase_time and now - self.phrase_time > timedelta(seconds=self.phrase_timeout):
                        phrase_complete = True
                    self.phrase_time = now

                    audio_data = b''.join(self.data_queue.queue)
                    self.data_queue.queue.clear()
                    text = self.process_audio(audio_data)

                    if phrase_complete:
                        translated_text = text_transcript(text=text)
                        self.transcription.append(translated_text)
                    else:
                        self.transcription[-1] = text

                    os.system('cls' if os.name == 'nt' else 'clear')
                    for line in self.transcription:
                        print(line)
                    print('', end='', flush=True)
                else:
                    sleep(0.25)
            except KeyboardInterrupt:
                break

        print("\n\nTranscription:")
        for line in self.transcription:
            print(line)


if __name__ == "__main__":
    translator = RealTimeSpeakerTranslator()
    translator.run()