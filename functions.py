from deep_translator import GoogleTranslator
import json
import requests
import speech_recognition as sr
from gtts import gTTS

def get_quote():
    response = requests.get("https://zenquotes.io/api/random")
    json_data = json.loads(response.text)
    quote = json_data[0]['q'] + " -" + json_data[0]['a']
    return(quote)

def translate_text(text, target):
    try:
        translated = GoogleTranslator(source='auto', target=target).translate(text)
        return translated
    except:
        return "ERROR"

def audiotext(filename):
    try:
        # Initialize the recognizer
        r = sr.Recognizer()

        # Open the file
        with sr.AudioFile(filename) as source:
            # Listen for the data (load audio to memory)
            audio_data = r.record(source)
            # Recognize (convert from speech to text)
            text = r.recognize_google(audio_data)
            return text
        
    except FileNotFoundError:
        return "Error: Audio file not found. Please make sure the file exists."
    except sr.UnknownValueError:
        return "Sorry, I couldn't recognize any speech in the audio."
    except sr.RequestError as e:
        return f"Error during recognition: {e}"
    
def texttomp3(text):
    myobj = gTTS(text=text, lang='en', slow=False)
    myobj.save("output.mp3")