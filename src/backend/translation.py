# Importing libraries
import os
from openai import AzureOpenAI
import re

# Adding functionality
languages_dict = {
    "Afrikaans": "af",
    "Arabic": "ar",
    "Bulgarian": "bg",
    "Bengali": "bn",
    "Catalan": "ca",
    "Czech": "cs",
    "Welsh": "cy",
    "Danish": "da",
    "German": "de",
    "Greek": "el",
    "English": "en",
    "Esperanto": "eo",
    "Spanish": "es",
    "Estonian": "et",
    "Persian": "fa",
    "Finnish": "fi",
    "French": "fr",
    "Gujarati": "gu",
    "Hebrew": "he",
    "Hindi": "hi",
    "Croatian": "hr",
    "Hungarian": "hu",
    "Indonesian": "id",
    "Icelandic": "is",
    "Italian": "it",
    "Japanese": "ja",
    "Javanese": "jv",
    "Kannada": "kn",
    "Korean": "ko",
    "Lithuanian": "lt",
    "Latvian": "lv",
    "Malayalam": "ml",
    "Marathi": "mr",
    "Malay": "ms",
    "Maltese": "mt",
    "Nepali": "ne",
    "Dutch": "nl",
    "Norwegian": "no",
    "Polish": "pl",
    "Portuguese": "pt",
    "Romanian": "ro",
    "Russian": "ru",
    "Sinhala": "si",
    "Slovak": "sk",
    "Slovenian": "sl",
    "Albanian": "sq",
    "Serbian": "sr",
    "Swedish": "sv",
    "Swahili": "sw",
    "Tamil": "ta",
    "Telugu": "te",
    "Thai": "th",
    "Turkish": "tr",
    "Ukrainian": "uk",
    "Urdu": "ur"
}

def text_translation(text: str, output_language: str) -> str:
    """
    Translates the given text to the specified output language using Azure OpenAI.

    Parameters:
    text (str): The text to be translated.
    output_language (str): The language code of the desired output language (e.g., 'en' for English, 'es' for Spanish).

    Returns:
    str: The translated text.
    """

    client = AzureOpenAI(
            api_version=os.getenv("OPENAI_API_VERSION_"),
            azure_endpoint="https://genai-nexus.api.corpinter.net/apikey/",
            api_key=os.getenv("NEXUS_API_KEY_DDQ")
        )

    message_text = [{
        "role": "system",
        "content": f"""
        You are an expert translator providing real-time translations. Your objective is to translate as accurately as possible.
        Return only the translated text, without any additional information or explanations.

        Input:
        Text to translate: "{text}"
        Target language: "{output_language}"

        Task:
        Translate the provided text into the target language with the utmost precision.

        Output:
        """
    }]

    chat_completion = client.chat.completions.create(
        model="gpt4-turbo",
        messages=message_text,
        temperature=0.0
    )
    
    try:
        response = chat_completion.choices[0].message.content.strip()
    except:
        response = ' '
    
    return response

def text_transcript(text: str) -> str:
    """
    Translates the given text to Spanish using Azure OpenAI.

    Parameters:
    text (str): The text to be translated.

    Returns:
    str: The translated text in Spanish.
    """
    client = AzureOpenAI(
            api_version=os.getenv("OPENAI_API_VERSION_"),
            azure_endpoint="https://genai-nexus.api.corpinter.net/apikey/",
            api_key=os.getenv("NEXUS_API_KEY_DDQ")
        )

    message_text = [{
        "role": "system",
        "content": f"""
        You are an expert translator providing real-time translations. Your objective is to translate as accurately as possible while preserving the original tone and formalities.
        Precision is key to avoid misunderstandings.

        Input:
        Text to translate: "{text}"

        Task:
        Translate the provided text into Spanish with the utmost precision, maintaining the tone and formalities of the original text.
        Return only the translated text, without any additional information.

        Output:
        The translated text in Spanish.
        """
    }]

    chat_completion = client.chat.completions.create(
        model="gpt4-turbo",
        messages=message_text,
        temperature=0.0
    )
    
    response = chat_completion.choices[0].message.content
    
    return response

def organise_transcript(text: str) -> str:
    """
    Translates the given text to Spanish using Azure OpenAI and organises the transcript.

    Parameters:
    text (str): The text to be translated.

    Returns:
    str: The translated text in Spanish.
    """
    client = AzureOpenAI(
        api_version=os.getenv("OPENAI_API_VERSION_"),
        azure_endpoint="https://genai-nexus.api.corpinter.net/apikey/",
        api_key=os.getenv("NEXUS_API_KEY_DDQ")
    )
        
    message_text = [{
        "role": "system",
        "content": f"""
        You are an expert translator providing real-time transcript. 
        Your objective is to translate as accurately as possible while preserving the original tone and formalities.
        Precision is key to avoid misunderstandings.
        In addition, there might be duplicate sentences because of the real time audio to text model. 
        Organise the final transcript so there is no duplicates and it represents reality as accurately as possible.

        It is important to keep the flow of the conversation, which is Surname, name (number): text, do not merge different phrases.

        Input:
        Transcript: "{text}"

        Task:
        Translate the provided text into Spanish with the utmost precision, maintaining the tone and formalities of the original text.
        Return only the transcript in Spanish, without any additional information.

        Output:
        The translated text in Spanish.
        """
    }]

    chat_completion = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=message_text,
        temperature=0.0
    )

    response = chat_completion.choices[0].message.content
    
    return response

def organise_buffer(buffer: str, text: str) -> str:
    """
    Translates the given text to Spanish using Azure OpenAI and organizes the transcript.

    Parameters:
    buffer (str): The existing transcript buffer.
    text (str): The new text to be translated and merged into the buffer.

    Returns:
    str: The translated and organized transcript in Spanish.
    """
    client = AzureOpenAI(
        api_version=os.getenv("OPENAI_API_VERSION_"),
        azure_endpoint="https://genai-nexus.api.corpinter.net/apikey/",
        api_key=os.getenv("NEXUS_API_KEY_DDQ")
    )
    
    message_text = [{
        "role": "system",
        "content": f"""
            You are an expert linguist providing real-time transcription services. 
            Your objective is to merge and organize the given transcripts, ensuring proper coherence and eliminating any duplicate messages.

            I will provide you with an existing transcript and new information. Your task is to assess any overlap and merge them accurately. 
            Ensure the final transcript is coherent, without duplicates, and accurately represents the original content.

            Input:
            Existing Transcript: "{buffer}"
            New Information: "{text}"

            Task:
            Translate the final merged transcript to Spanish with utmost precision, maintaining the original tone and formalities.
            Return only the translated transcript in Spanish, without any additional information.

            Output:
            The final transcript in Spanish.
        """
    }]

    chat_completion = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=message_text,
        temperature=0.0
    )
    response = chat_completion.choices[0].message.content.strip()
    
    return response

def format_transcript_markdown(transcript: str) -> str:
    """
    Formats the transcript into Markdown based on the specified pattern.

    Parameters:
    transcript (str): The transcript to be formatted.

    Returns:
    str: The formatted transcript in Markdown.
    """
    # Pattern to match the names and messages
    pattern = r"([A-ZÁÉÍÓÚÑ][a-záéíóúñ]+(?: [A-ZÁÉÍÓÚÑ][a-záéíóúñ]+)*, [A-ZÁÉÍÓÚÑ][a-záéíóúñ]+ \(\d+\))(.*?)(?=([A-ZÁÉÍÓÚÑ][a-záéíóúñ]+(?: [A-ZÁÉÍÓÚÑ][a-záéíóúñ]+)*, [A-ZÁÉÍÓÚÑ][a-záéíóúñ]+ \(\d+\))|$)"
    matches = re.findall(pattern, transcript, re.DOTALL)
    
    formatted_lines = []

    for match in matches:
        name, message, _ = match
        name = name.strip()
        message = message.strip()
        formatted_lines.append(f"**{name}**\n{message}")

    return '\n\n'.join(formatted_lines)

if __name__ =="__main__":
    transcript = """
      Bien, ahora estás trabajando: Veamos si podemos comenzar a procesar esto. Durán Álvarez, Sergio (638) ¿Qué demonios? ¿No estás mostrando nada? Durán Sergio (638) Solo por si acaso: ¿Por qué Álvarez? Durán Álvarez, Sergio (638) Solo por si acaso. Durán Sergio (638) De acuerdo Álvarez. Solo por si acaso. Durán Álvarez, Sergio (638) De acuerdo. Durán Álvarez, Sergio (638) Veamos si ahora podemos"""
    formatted_transcript = format_transcript_markdown(transcript)
    print(formatted_transcript)