from gtts import gTTS
import os
import tempfile

def speak_gtts(text, lang='en'):
    tts = gTTS(text=text, lang=lang)
    temp_path = os.path.join(tempfile.gettempdir(), "output.mp3")
    tts.save(temp_path)
    return temp_path  # Return audio file path
