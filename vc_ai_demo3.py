import streamlit as st
import requests
import base64
import json

# Zoom OAuth credentials (replace with your own)
CLIENT_ID = 'fhTNVEMTLGjbswpuumQ6Q'
CLIENT_SECRET = '32l1eslYqGoHiY7a6ugFl3Xh389snwbe'
REDIRECT_URI = 'https://efdemo.streamlit.app/'  # Your Redirect URI

# Step 1: Authorize the app
auth_url = f"https://zoom.us/oauth/authorize?response_type=code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}"

st.title("VC AI Agent Demo with OAuth")

query_params = st.experimental_get_query_params()

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
            "type": 1,
            "settings": {
                "join_before_host": True,
                "participant_video": False,
                "host_video": False,
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
        else:
            st.error("Error creating Zoom meeting. Please check the API response.")
            st.write(meeting_details)
    else:
        st.error("Error obtaining access token. Please check the response.")
        st.write(tokens)