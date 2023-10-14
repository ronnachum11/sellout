# initialize call

from twilio.rest import Client
import os

# Your Twilio account SID and Auth Token
account_sid = 'ACfdda12c5b78e66cc13365fcce8818585'
auth_token = '19627121e9b6024da63d5c86152904b5'

# Initialize the Twilio Client
client = Client(account_sid, auth_token)

# Read the text from a file
file_path = 'test.txt'
with open(file_path, 'r') as file:
    text_to_read = file.read()

# Using TwiML for making a call
from twilio.twiml.voice_response import VoiceResponse, Say

def generate_twiml(text):
    return str('''<?xml version="1.0" encoding="UTF-8"?>
               <Response>
               <Gather input="speech" action="https://e66f-24-23-158-128.ngrok-free.app/handle-input" method="POST" speechTimeout="auto">
               <Say>''' + text + '''</Say>
               </Gather>
               </Response>'''
)

# Generate TwiML
twiml = generate_twiml(text_to_read)
print(twiml)

# Make a call using the Twilio API
call = client.calls.create(
    twiml=twiml,
    to='+17043510608',
    from_='+18552200409'
)

# update call with additional response
# twiml = generate_twiml
# call = client.calls(call.sid).update(
#     twiml=twiml
#     method='POST'
# )

