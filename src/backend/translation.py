# Importing libraries
import os
from openai import AzureOpenAI

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

def text_translation(text:str, output_language:str)-> str:
    """
        Translates the given text to the specified output language using Azure OpenAI.

        Parameters:
        text (str): The text to be translated.
        output_language (str): The language code of the desired output language (e.g., 'en' for English, 'es' for Spanish).

        Returns:
        str: The translated text. 
    """

    client = AzureOpenAI(
        api_version = os.getenv("OPENAI_API_VERSION"),
        azure_endpoint=os.getenv("OPENAI_ENDPOINT"),
        api_key=os.getenv("OPENAI_KEY")
    )

    message_text = [{
    "role": "system",
    "content": f"""
        You are an expert translator providing real-time translations. Your objective is to translate as accurately as possible while preserving the original tone and formalities.
        Precision is key to avoid misunderstandings.

        Input:
        Text to translate: "{text}"
        Target language: "{output_language}"

        Task:
        Translate the provided text into the target language with the utmost precision, maintaining the tone and formalities of the original text.
        Return only the translated text, without any additional information.

        Output:
        The translated text in the target language.
    """
    }]

    chat_completion = client.chat.completions.create(
        model="gpt4-turbo",
        messages = message_text,
        temperature=0.0
    )
    
    response = chat_completion.choices[0].message.content
    
    return(response)


def text_transcript(text: str) -> str:
    """
    Translates the given text to Spanish using Azure OpenAI.

    Parameters:
    text (str): The text to be translated.

    Returns:
    str: The translated text in Spanish.
    """
    client = AzureOpenAI(
        api_version=os.getenv("OPENAI_API_VERSION"),
        azure_endpoint=os.getenv("OPENAI_ENDPOINT"),
        api_key=os.getenv("OPENAI_KEY")
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