# to get server address: ngrok http 127.0.0.1:5000

from flask import Flask, request
app = Flask(__name__)

@app.route("/handle-input", methods=['POST'])
def handle_input():
    # Get the digits input by the user during the call
    transcription_text = request.values.get("SpeechResult", "")
    
    print(transcription_text)
    # Write input to a text file
    with open("received.txt", "a") as file:
        file.write(transcription_text + "\n")
    
    # Respond to Twilio with further instructions (if needed)
    response = """<?xml version="1.0" encoding="UTF-8"?>
    <Response>
        <Say>Thank you. Your input has been received.</Say>
    </Response>
    """
    return response, {'Content-Type': 'text/xml'}

# Run the Flask app
if __name__ == "__main__":
    app.run(port=5000)
