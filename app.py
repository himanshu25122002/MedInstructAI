# app.py
import streamlit as st
from utils.ocr import extract_text_from_pdf, extract_text_from_image
from ask_llm import ask_ollama
from gtts_speak import speak_gtts
from voice_chat import lang_map
import tempfile
import os
from streamlit_mic import record_voice
from utils.translate import translate_to

# ✅ Risk alert system
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

# ✅ Init conversation memory
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "ask_clicked" not in st.session_state:
    st.session_state.ask_clicked = False

if "initial_response" not in st.session_state:
    st.session_state.initial_response = ""


if "exit_requested" not in st.session_state:
    st.session_state.exit_requested = False

st.set_page_config(page_title="MedInstructAI", page_icon="🩺")
st.title("🩺 MedInstructAI – Multilingual Voice/Text Medical Assistant")
st.caption("Explain medical reports in simple language. Speak or type your questions.")

# ✅ Step 1: Output Language Selection
lang_labels = {k: v[0] for k, v in lang_map.items()}
lang_choice = st.selectbox("🌐 Choose Output Language:", options=list(lang_labels.keys()), format_func=lambda k: lang_labels[k])
output_lang_name, stt_lang_code = lang_map[lang_choice]
target_lang_code = stt_lang_code.split("-")[0]  # e.g., "hi" from "hi-IN"


# ✅ Step 2: Input Method
input_method = st.radio("💬 How would you like to ask?", ["Type or Upload (PDF/Image)", "Speak"])
user_query = ""

if input_method == "Type or Upload (PDF/Image)":
    method = st.radio("📄 Select type: ", ["Type Text", "Upload PDF", "Upload Image"])
    if method == "Type Text":
        user_query = st.text_area("✍️ Enter your question or report:")
    elif method == "Upload PDF":
        uploaded_pdf = st.file_uploader("📄 Upload PDF report", type=["pdf"])
        if uploaded_pdf:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(uploaded_pdf.read())
                user_query = extract_text_from_pdf(tmp.name)
                os.unlink(tmp.name)
    elif method == "Upload Image":
        uploaded_image = st.file_uploader("🖼️ Upload image report", type=["jpg", "jpeg", "png"])
        if uploaded_image:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                tmp.write(uploaded_image.read())
                user_query = extract_text_from_image(tmp.name)
                os.unlink(tmp.name)
else:
    st.markdown("🎤 Speak your medical query:")
    user_query = record_voice()
    st.write("🗣️ You said:", user_query)


# ✅ Ask initial query
if st.button("🤖 Ask MedInstructAI") and user_query.strip():
    st.session_state.chat_history.append(("User", user_query.strip()))
    st.session_state.ask_clicked = True
    


    prompt = f"""
You are MedInstructAI, a trusted AI doctor assistant.

ONLY answer based on the exact user query provided.

DO NOT assume any report is uploaded unless clearly mentioned.

Strictly explain only: \"{user_query.strip()}\" 

Use simple, kind, and layman-friendly English like a village doctor.

Do NOT include any technical or medical jargon.

Always reply only in English. The system will handle translation.

Conversation so far:
"""

    for role, msg in st.session_state.chat_history:
        prompt += f"{role}: {msg}\n"
    prompt += "AI:"

    with st.spinner("💡 Thinking..."):
        response = ask_ollama(prompt)

    st.session_state.chat_history.append(("AI", response))
    # Translate only if not English
    if target_lang_code != "en":
        response_translated = translate_to(response, target_lang_code)
    else:
        response_translated = response

    st.session_state.initial_response = response_translated


if st.session_state.ask_clicked and st.session_state.initial_response:
    st.markdown("### 💬 MedInstructAI says:")
    st.write(st.session_state.initial_response)

    if check_for_risks(st.session_state.initial_response):
        st.error("⚠️ This response mentions serious medical risks. Please consult a doctor immediately!")

    if st.checkbox("🔊 Listen to the response", key="tts_initial"):
        audio_path = speak_gtts(st.session_state.initial_response, lang=stt_lang_code.split("-")[0])
        with open(audio_path, "rb") as audio_file:
            st.audio(audio_file.read(), format="audio/mp3")



# ✅ Follow-up questions (loop while user wants to continue)
if len(st.session_state.chat_history) > 0 and not st.session_state.exit_requested:
    st.markdown("---")
    st.markdown("### 🔁 Ask a follow-up question:")

    followup_mode = st.radio("Choose how to ask follow-up:", ["Type", "Speak"], horizontal=True)

    if followup_mode == "Type":
        followup_text = st.text_input("💬 Your follow-up (type 'exit' to stop):", key="followup_input")
    else:
        st.markdown("🎤 Speak your follow-up:")
        followup_text = record_voice()
        st.write("🗣️ You said:", followup_text)

    if followup_text:
        if followup_text.strip().lower() in ["exit", "no", "stop", "thanks", "thank you"]:
            st.success("👋 Exiting. Stay healthy!")
            st.session_state.exit_requested = True
        else:
            st.session_state.chat_history.append(("User", followup_text.strip()))

            prompt = f"""
You are MedInstructAI, a trusted AI doctor assistant.

ONLY answer based on the exact user query provided.

DO NOT assume any report is uploaded unless clearly mentioned.

Strictly explain only: \"{followup_text.strip()}\"  

Use simple, kind, and layman-friendly English like a village doctor.

Do NOT include any technical or medical jargon.

Always reply only in English. The system will handle translation.

Conversation so far:
"""

            for role, msg in st.session_state.chat_history:
                prompt += f"{role}: {msg}\n"
            prompt += "AI:"

            with st.spinner("💡 Thinking..."):
                response = ask_ollama(prompt)

# ✅ Translate if language is not English
            if stt_lang_code.split("-")[0] != "en":
                translated_response = translate_to(response, stt_lang_code.split("-")[0])
            else:
                translated_response = response

# ✅ Store and display
            st.session_state.chat_history.append(("AI", translated_response))
            st.markdown("### 💬 MedInstructAI says:")
            st.write(translated_response)

            if check_for_risks(translated_response):
                st.error("⚠️ This response mentions serious medical risks. Please consult a doctor immediately!")

            if st.checkbox("🔊 Listen to the response"):
                audio_path = speak_gtts(translated_response, lang=stt_lang_code.split("-")[0])
                with open(audio_path, "rb") as audio_file:
                    st.audio(audio_file.read(), format="audio/mp3")



# ✅ Display chat history
with st.expander("🗂️ Chat History"):
    for role, msg in st.session_state.chat_history:
        st.markdown(f"**{role}**: {msg}")