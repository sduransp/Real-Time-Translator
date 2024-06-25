# Real-Time-Translator
This is an ongoing personal project for translating in real-time to any language, using the same voice as the input (voice cloned)

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
