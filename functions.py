from deep_translator import GoogleTranslator
import json
import requests

def get_quote():
    response = requests.get("https://zenquotes.io/api/random")
    json_data = json.loads(response.text)
    quote = json_data[0]['q'] + " -" + json_data[0]['a']
    return(quote)

def translate_text(text):
    translated = GoogleTranslator(source='auto', target='de').translate(text)
    return translated