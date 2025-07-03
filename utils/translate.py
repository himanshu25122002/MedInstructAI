# utils/translate.py
from deep_translator import GoogleTranslator

def translate_to(text, target_lang):
    try:
        return GoogleTranslator(target=target_lang).translate(text)
    except Exception as e:
        print("Translation error:", e)
        return text
