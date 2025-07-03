from utils.input_handler import get_input_text
from ask_llm import ask_ollama
from gtts_speak import speak_gtts
from voice_chat import listen_to_user, lang_map
from termcolor import cprint

# ✅ Conversation memory to enable follow-up understanding
chat_history = []

def get_output_language():
    print("Choose output language:")
    for k, v in lang_map.items():
        print(f"{k}. {v[0]}")
    choice = input("Enter choice (1-10): ")
    return lang_map.get(choice, ("English", "en-IN"))

def get_user_input(input_lang_code):
    print("\nHow do you want to ask?")
    print("1. Type or upload (text/PDF/image)")
    print("2. Speak")
    method = input("Enter choice (1/2): ")

    if method == "2":
        return listen_to_user(input_lang_code)
    else:
        return get_input_text()

# ✅ Builds prompt with history included
def build_prompt(user_query, output_lang_name):
    chat_history.append(("User", user_query.strip()))
    prompt = f"""
You are MedInstructAI, a trusted AI doctor assistant.

ONLY answer based on the exact user query provided.

DO NOT assume any report is uploaded unless clearly mentioned.

Strictly explain only: "{user_query.strip()}"

Use friendly and simple language like a village doctor, but do not invent unrelated medical information.

Answer only in {output_lang_name}. Do not explain anything else.

Conversation so far:
"""
    for role, text in chat_history:
        prompt += f"{role}: {text}\n"
    prompt += "AI:"
    return prompt

def check_for_risks(response_text):
    danger_keywords = [
        "stroke", "heart attack", "heart failure", "emergency", "seizure",
        "tumor", "cancer", "kidney failure", "bleeding", "infection", "coma",
        "ICU", "ventilator", "life-threatening", "brain damage", "severe"
    ]
    response_lower = response_text.lower()
    for word in danger_keywords:
        if word in response_lower:
            return True
    return False

def main():
    print("\n🩺 Welcome to MedInstructAI (Multilingual Voice/Text Assistant)\n")

    output_lang_name, stt_lang_code = get_output_language()
    user_query = get_user_input(stt_lang_code)
    while True:
        if not user_query:
            continue

        # ✅ Use chat memory to build smarter prompt
        prompt = build_prompt(user_query, output_lang_name)

        print("\n💬 MedInstructAI says:\n")
        response = ask_ollama(prompt)
        print(response)

        # ✅ Store AI response to keep chat going
        chat_history.append(("AI", response))

        if check_for_risks(response):
            cprint("\n⚠️  WARNING: This response contains serious medical terms. "
                   "Please consult a healthcare professional immediately!", "red", attrs=["bold"])
            
        speak_choice = input("\n🔊 Do you want to listen to this response? (y/n): ").lower()
        if speak_choice == "y":
            speak_gtts(response, lang=stt_lang_code.split("-")[0])

        # 🔁 Follow-up input
        print("\n🔁 You may ask a follow-up question (or type 'exit' to stop)...")
        followup_method = input("1. Type  2. Speak: ")

        if followup_method == "2":
            user_query = listen_to_user(stt_lang_code)
        else:
            user_query = input("💬 Your follow-up: ")

        # ⛔ Exit on command
        if user_query.strip().lower() in ["exit", "no", "stop", "thanks", "thank you"]:
            print("This is AI-generated. Consult a licensed doctor.")
            print("👋 Exiting. Stay healthy!")
            
            break

if __name__ == "__main__":
    main()
