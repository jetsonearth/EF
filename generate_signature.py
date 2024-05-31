import base64
import hashlib
import hmac
import time

def generate_signature(api_key, api_secret, meeting_number, role):
    ts = int(round(time.time() * 1000)) - 30000
    msg = f'{api_key}{meeting_number}{ts}{role}'
    message = base64.b64encode(msg.encode('utf-8'))
    secret = base64.b64encode(api_secret.encode('utf-8'))

    signature = hmac.new(secret, message, hashlib.sha256).digest()
    signature = base64.b64encode(signature).decode("utf-8")
    return f'{api_key}.{meeting_number}.{ts}.{role}.{signature}'

api_key = 'YOUR_API_KEY'
api_secret = 'YOUR_API_SECRET'
meeting_number = 'YOUR_MEETING_NUMBER'
role = 0  # 0 for attendee, 1 for host

signature = generate_signature(api_key, api_secret, meeting_number, role)
print(signature)
