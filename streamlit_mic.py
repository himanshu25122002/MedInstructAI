# streamlit_mic.py
import streamlit as st
from streamlit_webrtc import webrtc_streamer
import speech_recognition as sr
import tempfile
import av

# Callback function to process audio frames
def audio_frame_callback(frame: av.AudioFrame):
    pcm_data = frame.to_ndarray().flatten().tobytes()
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        f.write(pcm_data)
        wav_path = f.name

    r = sr.Recognizer()
    with sr.AudioFile(wav_path) as source:
        audio = r.record(source)
    try:
        text = r.recognize_google(audio)
        st.session_state.transcribed_text = text
    except:
        st.session_state.transcribed_text = "Sorry, could not understand audio"

def record_voice():
    st.markdown("🎙️ Press Start and speak your query")
    webrtc_streamer(
        key="speech",
        audio_receiver_size=1024,
        media_stream_constraints={"audio": True, "video": False},
        audio_frame_callback=audio_frame_callback,
    )
    return st.session_state.get("transcribed_text", "")
