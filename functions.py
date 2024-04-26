from deep_translator import GoogleTranslator
import json
import requests
import speech_recognition as sr
from PIL import Image
import pytesseract
from transformers import pipeline

def get_quote():
    response = requests.get("https://zenquotes.io/api/random")
    json_data = json.loads(response.text)
    quote = json_data[0]['q'] + " -" + json_data[0]['a']
    return(quote)

def translate_text(text):
    text = GoogleTranslator(source='auto', target='de').translate(text)
    return translated

def audiotext(filename):
    
    # initialize the recognizer
    r = sr.Recognizer()

    # open the file
    with sr.AudioFile(filename) as source:
        # listen for the data (load audio to memory)
        audio_data = r.record(source)
        # recognize (convert from speech to text)
        text = r.recognize_google(audio_data)
        return text



