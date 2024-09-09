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

class RealTimeTranscript:
    """
    RealTimeTranscript handles real-time speech recognition from speakers,
    translation to Spanish, and prints the text on the screen.

    Attributes:
        model_name (str): Whisper model to be used.
        energy_threshold (int): Energy threshold for speech recognition.
        record_timeout (int): Timeout duration for recording.
        phrase_timeout (int): Timeout duration for detecting phrase end.
        speaker_device_index (int): Speaker device index for audio input.
        phrase_time (datetime): Time of the last detected phrase.
        data_queue (Queue): Queue to store audio data.
        transcription (list): List to store transcriptions.
        recorder (Recognizer): Speech recognition instance.
        audio_model (WhisperModel): Whisper model for speech-to-text.
        p (PyAudio): PyAudio instance for handling audio input.
    """

    def __init__(self, model="tiny", energy_threshold=1000, record_timeout=3, phrase_timeout=3):
        """
        Initializes the RealTimeTranscript with the given parameters.
        """
        self.model_name = model
        self.energy_threshold = energy_threshold
        self.record_timeout = record_timeout
        self.phrase_timeout = phrase_timeout
        
        self.phrase_time = None
        self.data_queue = Queue()
        self.transcription = ['']

        self.recorder = sr.Recognizer()
        self.recorder.energy_threshold = energy_threshold
        self.recorder.dynamic_energy_threshold = False
        
        self.p = pyaudio.PyAudio()
        self.speaker_device_index = self.find_valid_input_device()
        self.setup_speaker()
        self.load_audio_model()

    def find_valid_input_device(self):
        """
        Finds a valid input device with channels available.
        """
        target_device_name = "Headset Microphone (Jabra EVOLV"
        print("Available audio devices:")
        for index in range(self.p.get_device_count()):
            info = self.p.get_device_info_by_index(index)
            print(f"Device Index: {index}, Device Name: {info['name']}, Channels: {info['maxInputChannels']}")
            if target_device_name in info['name'] and info['maxInputChannels'] > 0:
                return index
        raise ValueError(f"No valid input device found with name {target_device_name}.")

    def setup_speaker(self):
        """
        Sets up the speaker for audio input.
        """
        device_info = self.p.get_device_info_by_index(self.speaker_device_index)
        channels = device_info['maxInputChannels']
        
        if channels < 1:
            raise ValueError(f"The selected device does not support the required number of input channels: {channels}")
        
        self.stream = self.p.open(format=pyaudio.paInt16,
                                  channels=channels,
                                  rate=16000,
                                  input=True,
                                  input_device_index=self.speaker_device_index,
                                  frames_per_buffer=1024)
        print(f"Using speaker: {device_info['name']} with index {self.speaker_device_index} and channels: {channels}")

    def load_audio_model(self):
        """
        Loads the Whisper audio model.
        """
        if self.model_name != "large":
            self.model_name += ".en"
        self.audio_model = whisper.load_model(self.model_name)

    def record_callback(self, in_data, frame_count, time_info, status):
        """
        Callback function to handle audio data.
        
        Args:
            in_data (bytes): The audio data.
        """
        self.data_queue.put(in_data)
        return (in_data, pyaudio.paContinue)

    def start_listening(self):
        """
        Starts listening for audio input from the speaker.
        """
        self.stream.start_stream()
        print("Model loaded and listening started.\n")

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
        print(f"Transcription result: {result['text'].strip()}")
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
    translator = RealTimeTranscript()
    translator.run()
