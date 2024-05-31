import streamlit as st
import requests
import json
import pyaudio
import wave
import os
from vosk import Model, KaldiRecognizer
from transformers import pipeline
import pyttsx3
import base64

CLIENT_ID = 'fhTNVEMTLGjbswpuumQ6Q'
CLIENT_SECRET = '32l1eslYqGoHiY7a6ugFl3Xh389snwbe'
REDIRECT_URI = 'https://efdemo.streamlit.app/'  # Your Redirect URI

# Load Vosk model for speech-to-text
vosk_model = Model("model")  # Replace "model" with the path to your Vosk model

# Load Hugging Face model for text generation
nlp_model = pipeline("text-generation", model="gpt2")  # You can use a smaller model like distilgpt2

# Initialize pyttsx3 for text-to-speech
tts_engine = pyttsx3.init()

# Zoom OAuth URL
auth_url = f"https://zoom.us/oauth/authorize?response_type=code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&scope=meeting:write meeting:write:admin"

st.title("VC AI Agent Demo with OAuth")

query_params = st.experimental_get_query_params()

def record_audio(filename, duration=5):
    """Record audio for a given duration."""
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100

    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

    frames = []
    for _ in range(0, int(RATE / CHUNK * duration)):
        data = stream.read(CHUNK)
        frames.append(data)

    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(filename, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

def transcribe_audio(filename):
    """Transcribe audio using Vosk."""
    wf = wave.open(filename, "rb")
    rec = KaldiRecognizer(vosk_model, wf.getframerate())

    results = []
    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            results.append(rec.Result())
    results.append(rec.FinalResult())

    text = " ".join([json.loads(result)["text"] for result in results])
    return text

def synthesize_speech(text, output_filename):
    """Convert text to speech using pyttsx3."""
    tts_engine.save_to_file(text, output_filename)
    tts_engine.runAndWait()

def get_nlp_response(prompt):
    """Get a response from a pre-trained NLP model (Hugging Face)."""
    response = nlp_model(prompt, max_length=50)
    return response[0]["generated_text"].strip()

if 'code' not in query_params:
    # Display the form to collect user details
    with st.form(key='meeting_form'):
        name = st.text_input("Your Name")
        email = st.text_input("Your Email")
        question = st.text_area("What would you like to discuss?")
        submit_button = st.form_submit_button(label='Request a Meeting')

    if submit_button:
        st.write("Please authorize the app to use your Zoom account:")
        st.write(f"[Authorize here]({auth_url})")
else:
    # Step 2: Handle the redirect and exchange the code for an access token
    code = query_params['code'][0]

    token_url = "https://zoom.us/oauth/token"
    auth_string = f"{CLIENT_ID}:{CLIENT_SECRET}"
    b64_auth_string = base64.b64encode(auth_string.encode()).decode()

    headers = {
        "Authorization": f"Basic {b64_auth_string}",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI
    }

    response = requests.post(token_url, headers=headers, data=data)
    tokens = response.json()

    if 'access_token' in tokens:
        access_token = tokens['access_token']
        st.write("Access Token Obtained:", access_token)

        # Step 3: Use the access token to create a Zoom meeting
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        meeting_data = {
            "topic": "VC Intro Call",
            "type": 1,  # Instant meeting
            "settings": {
                "join_before_host": True,
                "participant_video": False,
                "host_video": True,
            }
        }

        response = requests.post("https://api.zoom.us/v2/users/me/meetings", headers=headers, json=meeting_data)
        meeting_details = response.json()

        if 'id' in meeting_details and 'start_url' in meeting_details and 'join_url' in meeting_details:
            st.write("Meeting created successfully!")
            st.write("Meeting ID:", meeting_details['id'])
            st.write("Start URL:", meeting_details['start_url'])
            st.write("Join URL:", meeting_details['join_url'])
            st.markdown(f'<iframe src="{meeting_details["join_url"]}" width="700" height="500"></iframe>', unsafe_allow_html=True)

            # AI Agent logic
            st.write("Recording audio for 5 seconds...")
            record_audio("input.wav")

            st.write("Transcribing audio...")
            transcript = transcribe_audio("input.wav")
            st.write("You said:", transcript)

            st.write("Generating AI response...")
            ai_response = get_nlp_response(transcript)
            st.write("AI says:", ai_response)

            st.write("Converting AI response to speech...")
            synthesize_speech(ai_response, "response.mp3")

            st.write("Playing AI response...")
            audio_file = open("response.mp3", "rb")
            st.audio(audio_file.read(), format="audio/mp3")
        else:
            st.error("Error creating Zoom meeting. Please check the API response.")
            st.write(meeting_details)
    else:
        st.error("Error obtaining access token. Please check the response.")
        st.write(tokens)
