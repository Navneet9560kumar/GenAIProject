import pyttsx3
import speech_recognition as sr
from decouple import config

class TextToSpeech:
    def __init__(self):
        self.engine = pyttsx3.init()
        voices = self.engine.getProperty('voices')
        self.engine.setProperty('voice', voices[config('DEFAULT_VOICE', cast=int)].id)
        self.engine.setProperty('rate', 150)  # Speed of speech
        
    def speak(self, text):
        """Convert text to speech"""
        self.engine.say(text)
        self.engine.runAndWait()
        
    def listen(self):
        """Listen to user speech and convert to text"""
        r = sr.Recognizer()
        with sr.Microphone() as source:
            print("Listening...")
            audio = r.listen(source)
            
        try:
            text = r.recognize_google(audio)
            print(f"You said: {text}")
            return text
        except Exception as e:
            print("Sorry, I didn't catch that")
            return ""