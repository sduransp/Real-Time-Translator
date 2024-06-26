import whisper
import pyaudio
import numpy as np
import time

def real_time_translation():
    model = whisper.load_model("base")

    # Configuración de PyAudio
    CHUNK = 1024  # Tamaño del bloque
    FORMAT = pyaudio.paInt16  # Formato de los datos
    CHANNELS = 1  # Número de canales
    RATE = 16000  # Tasa de muestreo
    RECORD_SECONDS = 2  # Número de segundos a acumular antes de transcribir
    SILENCE_THRESHOLD = 0.01  # Umbral de silencio

    # Inicialización de PyAudio
    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    print("Recording...")

    try:
        while True:
            print("Collecting audio...")
            frames = []

            for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
                data = stream.read(CHUNK, exception_on_overflow=False)
                audio_chunk = np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32768.0
                frames.append(audio_chunk)

            # Unir los fragmentos de audio acumulados
            audio = np.concatenate(frames)

            # Detectar y eliminar silencio
            if np.max(np.abs(audio)) > SILENCE_THRESHOLD:
                # Procesa el audio si supera el umbral de silencio
                audio = whisper.pad_or_trim(audio)

                # Crea el espectrograma log-Mel y muévelo al mismo dispositivo que el modelo
                mel = whisper.log_mel_spectrogram(audio).to(model.device)

                # Decodifica el audio asumiendo que el idioma es español
                options = whisper.DecodingOptions(language="es")
                result = whisper.decode(model, mel, options)

                # Imprime el texto reconocido
                print(result.text)
            else:
                print("Silence detected, skipping...")

            # Pausa breve para evitar solapamiento
            time.sleep(0.1)

    except KeyboardInterrupt:
        # Finaliza la grabación
        print("Stopping...")
        stream.stop_stream()
        stream.close()
        p.terminate()

real_time_translation()