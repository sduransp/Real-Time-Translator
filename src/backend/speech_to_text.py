import datetime
import logging
import os
import wave
import threading
import tempfile
import numpy as np
import sounddevice as sd
import whisper
import warnings
import queue
import sys

# Suppress the FP16 warning
warnings.filterwarnings("ignore", message="FP16 is not supported on CPU; using FP32 instead")

class RealTimeTranscriber:
    """
    A class to handle real-time audio transcription using Whisper.

    Attributes:
    -----------
    sample_rate : int
        The sample rate for the audio input.
    model : whisper.Model
        The Whisper model used for transcription.
    is_running : bool
        Flag to control the running state of the transcription.
    queue : queue.Queue
        Queue to hold audio chunks for processing.
    audio_queue : np.ndarray
        Array to accumulate audio data before processing.
    mutex : threading.Lock
        Mutex for thread-safe operations on audio_queue.
    chunk_size : int
        Size of each audio chunk (in samples).
    silence_threshold : float
        Threshold to detect silence based on audio energy.
    silence_duration : int
        Duration to consider as silence (in seconds).
    silence_buffer : int
        Number of samples representing the silence duration.
    silence_counter : int
        Counter to keep track of silence duration.
    recording_active : bool
        Flag to indicate if recording is currently active.
    audio_interface : sd.InputStream
        Audio input stream interface.
    transcription_thread : threading.Thread
        Thread to handle transcription in the background.
    """

    def __init__(self, model_name="base", sample_rate=16000, silence_threshold=0.005, silence_duration=1):
        """
        Initialize the RealTimeTranscriber with the specified model and parameters.

        Parameters:
        -----------
        model_name : str
            Name of the Whisper model to load.
        sample_rate : int
            Sample rate for the audio input.
        silence_threshold : float
            Threshold to detect silence based on audio energy.
        silence_duration : int
            Duration to consider as silence (in seconds).
        """
        self.sample_rate = sample_rate
        self.model = whisper.load_model(model_name)
        self.is_running = False
        self.queue = queue.Queue()
        self.audio_queue = np.ndarray([], dtype=np.float32)
        self.mutex = threading.Lock()
        self.chunk_size = self.sample_rate  # 1 second chunks
        self.silence_threshold = silence_threshold
        self.silence_duration = silence_duration
        self.silence_buffer = int(self.sample_rate * self.silence_duration)
        self.silence_counter = 0
        self.recording_active = False
        self.audio_interface = sd.InputStream(samplerate=self.sample_rate, channels=1, dtype="float32", callback=self.callback)

        # Start the transcription thread
        self.transcription_thread = threading.Thread(target=self.process_queue)
        self.transcription_thread.start()

    def callback(self, indata, frames, time, status):
        """
        Callback function to handle incoming audio data.

        Parameters:
        -----------
        indata : np.ndarray
            The incoming audio data.
        frames : int
            Number of frames in the audio data.
        time : CData
            Timing information.
        status : CallbackFlags
            Status flags.
        """
        with self.mutex:
            audio_chunk = indata.ravel()
            self.queue.put(audio_chunk)
            # print("Audio chunk added to queue")  # Debug message
            sys.stdout.flush()

    def is_silent(self, audio_chunk):
        """
        Check if the given audio chunk is silent based on the energy threshold.

        Parameters:
        -----------
        audio_chunk : np.ndarray
            The audio chunk to check.

        Returns:
        --------
        bool
            True if the audio chunk is silent, False otherwise.
        """
        energy = np.mean(np.abs(audio_chunk))
        # print(f"Energy: {energy}")  # Debug message
        return energy < self.silence_threshold

    def process_queue(self):
        """
        Process the audio chunks from the queue and handle recording state transitions.
        """
        while True:
            audio_chunk = self.queue.get()
            if audio_chunk is None:
                break

            if self.is_silent(audio_chunk):
                if self.recording_active:
                    self.silence_counter += len(audio_chunk)
                    if self.silence_counter >= self.silence_buffer:
                        self.recording_active = False
                        self.silence_counter = 0
                        if self.audio_queue.size > 0:
                            self.transcribe(np.concatenate([self.audio_queue]))
                        self.audio_queue = np.ndarray([], dtype=np.float32)
                # If not recording, do nothing
            else:
                if not self.recording_active:
                    self.audio_queue = np.ndarray([], dtype=np.float32)
                    self.recording_active = True
                self.silence_counter = 0
                self.audio_queue = np.append(self.audio_queue, audio_chunk)

    def transcribe(self, audio_chunk):
        """
        Transcribe the given audio chunk using the Whisper model.

        Parameters:
        -----------
        audio_chunk : np.ndarray
            The audio chunk to transcribe.
        """
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
            pcm_data = (audio_chunk * 32767).astype(np.int16).tobytes()
            with wave.open(temp_file.name, 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(self.sample_rate)
                wf.writeframes(pcm_data)
            temp_filename = temp_file.name
        try:
            print(f"Transcribing audio chunk from {temp_filename}")  # Debug message
            sys.stdout.flush()
            result = self.model.transcribe(temp_filename, language='es')
            print(f"Transcription result: {result['text']}")  # Debug message
            sys.stdout.flush()  # Force flush the output buffer
        except Exception as e:
            print(f"Error during transcription: {e}")
            sys.stdout.flush()
        finally:
            os.unlink(temp_filename)

    def start(self):
        """
        Start the audio stream and transcription process.
        """
        self.is_running = True
        with self.audio_interface as stream:
            print("Starting audio stream")  # Debug message
            sys.stdout.flush()
            while self.is_running:
                sd.sleep(1000)

    def stop(self):
        """
        Stop the audio stream and transcription process.
        """
        self.is_running = False
        self.queue.put(None)  # Send a signal to the transcription thread to stop
        self.transcription_thread.join()
        self.audio_interface.abort()
        print("Transcription stopped.")  # Debug message
        sys.stdout.flush()  # Force flush the output buffer

if __name__ == "__main__":
    transcriber = RealTimeTranscriber()
    try:
        transcriber.start()
    except KeyboardInterrupt:
        transcriber.stop()
        print("Transcription stopped by KeyboardInterrupt.")  # Debug message
        sys.stdout.flush()  # Force flush the output buffer