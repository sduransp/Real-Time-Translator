# Importing libraries
import os
from openai import AzureOpenAI

# Adding functionality

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