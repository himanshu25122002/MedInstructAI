import speech_recognition as sr

# Language name and Google STT codes
lang_map = {
    "1": ("English", "en-IN"),
    "2": ("Hindi", "hi-IN"),
    "3": ("Bhojpuri", "hi-IN"),   # Closest match
    "4": ("Marathi", "mr-IN"),
    "5": ("Gujarati", "gu-IN"),
    "6": ("Bengali", "bn-IN"),
    "7": ("Tamil", "ta-IN"),
    "8": ("Telugu", "te-IN"),
    "9": ("Kannada", "kn-IN"),
    "10": ("Malayalam", "ml-IN")
}

def listen_to_user(lang_code='hi-IN'):
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print(f"\n🎙️ Speak your query in {lang_code} (Ctrl+C to stop)...")
        audio = r.listen(source)
    try:
        text = r.recognize_google(audio, language=lang_code)
        print(f"\n🗣️ You said: {text}")
        return text
    except sr.UnknownValueError:
        print("❌ Could not understand audio")
        return ""
    except sr.RequestError:
        print("❌ Google STT service error")
        return ""
