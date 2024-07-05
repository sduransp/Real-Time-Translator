# Real-Time Multilingual Conversation Translator for MS Teams

Welcome to the Real-Time Multilingual Conversation Translator for MS Teams! This project aims to break language barriers in virtual meetings by providing real-time translations of conversations from Microsoft Teams into Spanish and enabling users to speak in Spanish while their speech is translated and sent back in the target language. With this app, you can effortlessly engage in conversations in any language on MS Teams.

## Key Features

* **Real-Time Translation:** Translates conversations from MS Teams into Spanish in real-time.
* **Speech Synthesis:** Converts Spanish text back into the target language and generates speech.
* **Two-Way Communication:** Facilitates seamless two-way communication by allowing you to speak in Spanish and have your speech translated and sent in the target language.
* **Multi-Language Support:** Supports multiple target languages for translation, making it versatile for diverse communication needs.

## How It Works

1. **Listening to MS Teams Conversations:** The app listens to conversations happening in MS Teams.
2. **Real-Time Transcription:** It transcribes the spoken language into text.
3. **Translation to Spanish:** The transcribed text is translated into Spanish.
4. **Displaying on Screen:** The translated Spanish text is displayed on your screen in real-time.
5. **Speaking in Spanish:** When you speak in Spanish, your speech is transcribed to text.
6. **Translation to Target Language:** The Spanish text is translated into the target language.
7. **Speech Synthesis:** The translated text is converted into speech.
8. **Sending Back to MS Teams:** The synthesized speech is sent back to MS Teams, allowing the other participants to hear it in their native language.

## Installation

### Clone repository

```bash
git clone https://github.com/yourusername/real-time-teams-translator.git
cd real-time-teams-translator
```

### Install dependencies

```bash
pip install -r requirements.txt
```
### Set up environments variables

```bash
OPENAI_API_VERSION=your_api_version
OPENAI_ENDPOINT=your_openai_endpoint
OPENAI_KEY=your_openai_key
```
### Run

```bash
python app.py
```

## Usage

1. **Start the App:** Launch the application to begin listening to MS Teams conversations.
2. **Monitor Translations:** The app will display real-time translations of the conversation in Spanish on your screen.
3. **Speak in Spanish:** Use your microphone to speak in Spanish.
4. **Hear Translations:** The app will translate your Spanish speech to the target language and send it as synthesized speech back to MS Teams.

## Tech Stack

* **Whisper:** For speech-to-text transcription.
* **Azure OpenAI:** For text translation.
* **TTS (Text-to-Speech):** For speech synthesis.
* **PyAudio:** For handling audio input and output.
* **SpeechRecognition:** For capturing audio from the microphone.

To set up and run the project, follow these steps:

```bash
voice-cloning-translation-app/
├── .github/
│   └── workflows/
│       └── ci.yml  # Configuraciones de integración continua (opcional)
├── docs/
│   └── README.md  # Documentación detallada del proyecto
├── src/
│   ├── frontend/
│   │   ├── __init__.py
│   │   ├── app.py  # Código para la interfaz de usuario
│   │   ├── static/
│   │   └── templates/
│   │       └── index.html  # Página principal de la aplicación
│   ├── backend/
│   │   ├── __init__.py
│   │   ├── main.py  # Punto de entrada para el backend
│   │   ├── speech_to_text.py  # Código para convertir voz a texto usando Hugging Face
│   │   ├── voice_cloning.py  # Código para clonar la voz usando Hugging Face
│   │   └── translation.py  # Código para traducir texto usando OpenAI
│   ├── config/
│   │   └── config.yaml  # Configuraciones de la aplicación (API keys, etc.)
├── tests/
│   ├── __init__.py
│   ├── test_frontend.py  # Pruebas para el frontend
│   ├── test_backend.py  # Pruebas para el backend
│   └── test_integration.py  # Pruebas de integración
├── .gitignore
├── requirements.txt  # Dependencias del proyecto
├── setup.py  # Script de instalación
└── README.md  # Instrucciones básicas del proyecto
```
