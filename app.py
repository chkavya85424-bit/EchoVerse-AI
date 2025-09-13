import streamlit as st
from transformers import pipeline
from gtts import gTTS
import subprocess
import os
from pathlib import Path

# ----------------------------
# Setup
# ----------------------------
st.set_page_config(page_title="EchoVerse", layout="wide")
output_dir = Path("outputs")
output_dir.mkdir(exist_ok=True)

# Load Hugging Face model for rewriting text
rewrite_model = pipeline("text2text-generation", model="google/flan-t5-base")

# ----------------------------
# Helper functions
# ----------------------------
def rewrite_text(text, tone):
    prompt = f"Rewrite the following text in a {tone} tone, keeping the original meaning:\n\n{text}"
    result = rewrite_model(prompt, max_length=512, num_return_sequences=1)
    return result[0]["generated_text"]

def text_to_speech(text, filename="output.mp3"):
    # Use gTTS to create speech in mp3 format
    tts = gTTS(text)
    wav_file = output_dir / "temp.wav"
    mp3_file = output_dir / filename

    # Save as wav first
    tts.save(str(wav_file))

    # Convert wav → mp3 with ffmpeg
    subprocess.run([
        "ffmpeg", "-y", "-i", str(wav_file), str(mp3_file)
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Cleanup
    if wav_file.exists():
        wav_file.unlink()

    return mp3_file

# ----------------------------
# Streamlit UI
# ----------------------------
st.title("🎧 EchoVerse – AI-Powered Audiobook Creator")

st.write("Upload text or paste below, choose a tone and voice, then generate expressive audio narration.")

# Text input
uploaded_file = st.file_uploader("Upload a .txt file", type="txt")
user_text = st.text_area("Or paste your text here:", height=200)

if uploaded_file:
    user_text = uploaded_file.read().decode("utf-8")

tone = st.selectbox("Choose tone", ["Neutral", "Suspenseful", "Inspiring"])
voice = st.selectbox("Choose voice", ["Default (gTTS)"])  # Placeholder for more voices

if st.button("Generate Audiobook"):
    if user_text.strip():
        st.subheader("Original Text")
        st.write(user_text)

        # Rewrite with tone
        rewritten = rewrite_text(user_text, tone)

        st.subheader(f"{tone} Version")
        st.write(rewritten)

        # Generate speech
        st.info("Generating audio, please wait...")
        audio_file = text_to_speech(rewritten, "audiobook.mp3")

        # Audio player
        st.audio(str(audio_file), format="audio/mp3")

        # Download button
        with open(audio_file, "rb") as f:
            st.download_button(
                label="📥 Download MP3",
                data=f,
                file_name="audiobook.mp3",
                mime="audio/mp3"
            )
    else:
        st.warning("Please provide some text first!")


