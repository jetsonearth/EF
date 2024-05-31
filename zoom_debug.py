import requests
import jwt
import time
import json

# Zoom API credentials (replace with your own)
API_KEY = 'H6VyMtjWQV2VNr2JwAQNDA'
API_SECRET = 'zpqivmGpbBbo7YsVg4zRBHiu0UKgAcMz'

# Function to generate a JWT token
def generate_jwt():
    payload = {
        'iss': API_KEY,
        'exp': time.time() + 3600  # Token expires in 1 hour
    }
    token = jwt.encode(payload, API_SECRET, algorithm='HS256')
    return token

# Decode the JWT to verify its contents
def decode_jwt(token):
    decoded = jwt.decode(token, API_SECRET, algorithms=['HS256'])
    return decoded

# Function to create a Zoom meeting
def create_zoom_meeting():
    url = "https://api.zoom.us/v2/users/me/meetings"
    headers = {
        "Authorization": f"Bearer {generate_jwt()}",
        "Content-Type": "application/json"
    }
    payload = {
        "topic": "VC Intro Call",
        "type": 1,
        "settings": {
            "join_before_host": True,
            "participant_video": False,
            "host_video": False,
        }
    }
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    meeting_details = response.json()

    # Log the full response for debugging
    print("Zoom API response:", json.dumps(meeting_details, indent=4))

    if 'id' in meeting_details and 'start_url' in meeting_details and 'join_url' in meeting_details:
        return meeting_details['id'], meeting_details['start_url'], meeting_details['join_url']
    else:
        print("Error creating Zoom meeting: Missing expected keys in the response")
        return None, None, None

# Generate JWT and test creating a Zoom meeting
jwt_token = generate_jwt()
print("Generated JWT:", jwt_token)

decoded_token = decode_jwt(jwt_token)
print("Decoded JWT:", decoded_token)

meeting_number, start_url, join_url = create_zoom_meeting()
if meeting_number:
    print(f"Meeting Number: {meeting_number}")
    print(f"Start URL: {start_url}")
    print(f"Join URL: {join_url}")
