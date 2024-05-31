import streamlit as st
from zoomus import ZoomClient
import pyttsx3
import time

# Zoom API credentials (replace with your own)
API_KEY = 'your_zoom_api_key'
API_SECRET = 'your_zoom_api_secret'

client = ZoomClient(API_KEY, API_SECRET)
engine = pyttsx3.init()

def create_zoom_meeting():
    user_list = client.user.list()
    user_id = user_list['users'][0]['id']
    meeting_details = {
        'topic': 'VC Intro Call',
        'type': 1,
        'settings': {
            'join_before_host': True,
            'participant_video': False,
            'host_video': False,
        }
    }
    meeting = client.meeting.create(user_id=user_id, **meeting_details)
    return meeting['join_url']

def ai_conversation():
    engine.say("Hello, I am your AI assistant. How can I help you today?")
    engine.runAndWait()

st.title("VC AI Agent Demo")

with st.form(key='meeting_form'):
    name = st.text_input("Your Name")
    email = st.text_input("Your Email")
    question = st.text_area("What would you like to discuss?")
    submit_button = st.form_submit_button(label='Request a Meeting')

if submit_button:
    meeting_url = create_zoom_meeting()
    st.success(f"Meeting created! You can join using the following link: {meeting_url}")
    st.markdown(f"[Join Meeting]({meeting_url})")
    
    st.write("The AI agent will join the meeting shortly.")
    # Simulate the AI joining the meet
