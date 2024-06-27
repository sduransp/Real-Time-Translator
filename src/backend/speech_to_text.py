import argparse
import os
import numpy as np
import speech_recognition as sr
import whisper
import torch
import simpleaudio as sa
from TTS.api import TTS
from pydub import AudioSegment
from io import BytesIO

from datetime import datetime, timedelta
from queue import Queue
from time import sleep
from sys import platform

from translation import text_translation, languages_dict


class RealTimeTranslator:
    """
        A class to perform real-time speech recognition, translation, and text-to-speech synthesis.
    """
    def __init__(self, model="tiny", non_english=True, output_language="English", energy_threshold=1000, record_timeout=3, phrase_timeout=3, default_microphone='pulse'):
        """
            Initialize the RealTimeTranslator with the given parameters.

            Parameters:
            model (str): Whisper model to use (tiny, base, small, medium, large). Default is "tiny".
            non_english (bool): If set, does not use the English model. Default is True.
            output_language (str): The language for the output translation. Default is "English".
            energy_threshold (int): Energy level for the microphone to detect. Default is 1000.
            record_timeout (float): How real-time the recording is in seconds. Default is 3.
            phrase_timeout (float): How much empty space between recordings before considering it a new line in the transcription. Default is 3.
            default_microphone (str): Default microphone name for SpeechRecognition on Linux. Default is 'pulse'.
        """
        # Instantiating variables
        self.model_name = model
        self.non_english = non_english
        self.output_language = output_language
        self.energy_threshold = energy_threshold
        self.record_timeout = record_timeout
        self.phrase_timeout = phrase_timeout
        self.default_microphone = default_microphone

        self.phrase_time = None
        self.data_queue = Queue()
        self.transcription = ['']
        self.tts = TTS(model_name="tts_models/multilingual/multi-dataset/your_tts", progress_bar=False)

        self.recorder = sr.Recognizer()
        self.recorder.energy_threshold = energy_threshold
        self.recorder.dynamic_energy_threshold = False
        
        #Setting microphone and loading model
        self.setup_microphone()
        self.load_audio_model()

    def setup_microphone(self):
        """
            Setup the microphone for audio recording.
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
            Load the Whisper audio model.
        """
        if self.model_name != "large" and not self.non_english:
            self.model_name = self.model_name + ".en"
        self.audio_model = whisper.load_model(self.model_name)

    def record_callback(self, _, audio: sr.AudioData) -> None:
        """"
            Callback function to receive audio data when recordings finish.

            Parameters:
            audio (sr.AudioData): An AudioData containing the recorded bytes.
        """
        data = audio.get_raw_data()
        self.data_queue.put(data)

    def start_listening(self):
        """
            Start listening to the audio input and adjust for ambient noise.
        """
        with self.source:
            self.recorder.adjust_for_ambient_noise(self.source)
        self.recorder.listen_in_background(self.source, self.record_callback, phrase_time_limit=self.record_timeout)
        print("Model loaded.\n")

    def process_audio(self, audio_data):
        """
            Process the audio data and transcribe it using the Whisper model.

            Parameters:
            audio_data (bytes): Raw audio data.

            Returns:
            str: The transcribed text.
        """
        audio_np = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
        result = self.audio_model.transcribe(audio_np, fp16=torch.cuda.is_available())
        return result['text'].strip()

    def synthesize_and_play_audio(self, text):
        """
            Synthesize and play the audio from the given text.

            Parameters:
            text (str): The text to be converted to speech.
        """
        wav_buffer = BytesIO()
        self.tts.tts_to_file(text=text, file_path=wav_buffer, language=languages_dict[self.output_language], speaker="male-en-2")
        wav_buffer.seek(0)
        audio = AudioSegment.from_file(wav_buffer, format="wav")
        play_obj = sa.play_buffer(audio.raw_data, num_channels=audio.channels, bytes_per_sample=audio.sample_width, sample_rate=audio.frame_rate)
        play_obj.wait_done()

    def run(self):
        """
            Run the main loop to handle audio recording, processing, translation, and playback.
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