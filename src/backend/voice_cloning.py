import argparse
import os
import numpy as np
import speech_recognition as sr
import whisper
import torch
from TTS.api import TTS
from pydub import AudioSegment
from io import BytesIO
from datetime import datetime, timedelta
from queue import Queue
from time import sleep
from sys import platform
import pyaudio
from translation import text_translation, languages_dict


class RealTimeTranslator:
    """
    RealTimeTranslator handles real-time speech recognition, translation, and text-to-speech synthesis.
    
    Attributes:
        model_name (str): Whisper model to be used.
        non_english (bool): Whether the input language is non-English.
        output_language (str): Target language for translation.
        energy_threshold (int): Energy threshold for speech recognition.
        record_timeout (int): Timeout duration for recording.
        phrase_timeout (int): Timeout duration for detecting phrase end.
        default_microphone (str): Default microphone name.
        output_device_name (str): Output device name for audio playback.
        phrase_time (datetime): Time of the last detected phrase.
        data_queue (Queue): Queue to store audio data.
        transcription (list): List to store transcriptions.
        tts (TTS): Text-to-Speech synthesis instance.
        recorder (Recognizer): Speech recognition instance.
        source (Microphone): Microphone instance for audio input.
        audio_model (WhisperModel): Whisper model for speech-to-text.
        p (PyAudio): PyAudio instance for handling audio playback.
        output_device_index (int): Index of the output device.
    """

    def __init__(self, model="tiny", non_english=True, output_language="German", energy_threshold=1000, 
                 record_timeout=3, phrase_timeout=3, default_microphone='pulse', output_device=1):
        """
        Initializes the RealTimeTranslator with the given parameters.
        """
        self.model_name = model
        self.non_english = non_english
        self.output_language = output_language
        self.energy_threshold = energy_threshold
        self.record_timeout = record_timeout
        self.phrase_timeout = phrase_timeout
        self.default_microphone = default_microphone
        self.output_device_name = 'CABLE Input (2- VB-Audio Virtua' if output_device == 0 else 'Headset Earphone (Jabra EVOLVE'
        
        self.phrase_time = None
        self.data_queue = Queue()
        self.transcription = ['']

        self.tts = TTS(model_name=f"tts_models/{'de' if self.output_language == 'German' else 'en'}/ljspeech/tacotron2-DDC", 
                       progress_bar=False, gpu=True)

        self.recorder = sr.Recognizer()
        self.recorder.energy_threshold = energy_threshold
        self.recorder.dynamic_energy_threshold = False
        
        self.setup_microphone()
        self.load_audio_model()

        self.p = pyaudio.PyAudio()
        self.output_device_index = self.find_output_device_index()

    def setup_microphone(self):
        """
        Sets up the microphone for audio input.
        """
        if 'linux' in platform:
            mic_name = self.default_microphone
            if not mic_name or mic_name == 'list':
                print("Available microphone devices are: ")
                for index, name in enumerate(sr.Microphone.list_microphone_names()):
                    print(f"Microphone with name \"{name}\" found")
                return
            else:
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
        if self.model_name != "large" and not self.non_english:
            self.model_name += ".en"
        self.audio_model = whisper.load_model(self.model_name)

    def find_output_device_index(self):
        """
        Finds the output device index for audio playback.
        """
        for i in range(self.p.get_device_count()):
            info = self.p.get_device_info_by_index(i)
            if self.output_device_name in info['name']:
                print(f"Output device '{self.output_device_name}' found with index {i}")
                return i
        raise ValueError(f"Output device '{self.output_device_name}' not found")

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
        Starts listening for audio input.
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

    def synthesize_and_play_audio(self, text):
        """
        Synthesizes and plays the audio from the given text.
        
        Args:
            text (str): The text to synthesize.
        """
        wav_buffer = BytesIO()
        self.tts.tts_with_vc_to_file(
            text,
            speaker_wav=r"C:\Users\DURANAS\Coding\real-time-translator\data\voice\sergio_voice.mp3",
            file_path=wav_buffer
        )

        wav_buffer.seek(0)
        audio = AudioSegment.from_file(wav_buffer, format="wav")

        try:
            print(f"Synthesizing audio for text: {text}")

            stream = self.p.open(format=self.p.get_format_from_width(audio.sample_width),
                                 channels=audio.channels,
                                 rate=audio.frame_rate,
                                 output=True,
                                 output_device_index=self.output_device_index)

            stream.write(audio.raw_data)
            stream.stop_stream()
            stream.close()

            print("Audio successfully written to VB-Cable")
        except Exception as e:
            print(f"Error opening stream: {e}")

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
                        text = text_translation(text=text, output_language=self.output_language)
                        self.transcription.append(text)
                        self.synthesize_and_play_audio(text)
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
    translator = RealTimeTranslator()
    translator.run()