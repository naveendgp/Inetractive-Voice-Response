import os
from flask import Flask, request, jsonify
from twilio.twiml.voice_response import VoiceResponse, Gather
from twilio.twiml.messaging_response import MessagingResponse
from groq import Groq  # Ensure Groq package is installed and available

# Initialize Flask app
app = Flask(__name__)

# Set up Groq API key
GROQ_API_KEY = "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"

# Initialize Groq client
groq_client = Groq(api_key=GROQ_API_KEY)

def fetch_groq_response(prompt):
    """
    Fetches a response from the Groq API based on the provided prompt.
    """
    try:
        response = groq_client.chat.completions.create(
            messages=[
                {"role": "user", "content": prompt}
            ],
            model="llama3-8b-8192",  # Adjust the model based on your Groq setup
            stream=False
        )
        return response.choices[0].message.content.strip()
    except Exception as error:
        print(f"Groq API Error: {error}")
        return "I'm sorry, but I couldn't process your request at the moment."

@app.route("/voice", methods=['POST'])
def handle_voice_request():
    """
    Handles voice requests from Twilio. Processes speech input and responds using Groq API.
    """
    resp = VoiceResponse()

    # Check if a speech result is provided
    input_text = request.values.get('SpeechResult')
    if input_text:
        print(f"Received SpeechResult: {input_text}")

        # Get Groq's response
        groq_response = fetch_groq_response(input_text)
        print(f"Groq Voice Response: {groq_response}")

        # Respond with Groq's output
        resp.say(groq_response, voice='alice')
    else:
        # Initial or fallback response
        resp.say(
            "Welcome to Fam2Bag, your e-commerce AI assistant. How may I assist you today?",
            voice='alice'
        )

    # Prepare to gather additional speech input
    gather = Gather(
        input='speech',
        action='/voice',
        speech_timeout='auto',
        hints="hello,buy,sell,order,product names,help"
    )
    resp.append(gather)

    # Final fallback message if no input is received
    resp.say("Thank you for calling Fam2Bag. Goodbye!")
    return str(resp)

@app.route("/sms", methods=['POST'])
def handle_sms_request():
    """
    Handles SMS requests from Twilio. Processes the incoming message and responds using Groq API.
    """
    try:
        incoming_msg = request.form.get('Body', '').strip()
        if not incoming_msg:
            raise ValueError("No message content received.")

        print(f"Received SMS: {incoming_msg}")

        # Get Groq's response
        groq_response = fetch_groq_response(incoming_msg)
        print(f"Groq SMS Response: {groq_response}")

        # Respond back via SMS
        resp = MessagingResponse()
        resp.message(groq_response)
        return str(resp)
    except Exception as error:
        print(f"SMS Handling Error: {error}")
        resp = MessagingResponse()
        resp.message("Sorry, I couldn't process your request at the moment.")
        return str(resp)

@app.route("/demo", methods=['GET'])
def demo_endpoint():
    """
    A demo GET API for testing the server.
    """
    return jsonify({
        "status": "success",
        "message": "This is a demo endpoint!",
        "tips": "You can integrate this API with your client."
    })

if __name__ == "__main__":
    # Dynamically bind to a port if provided by the environment (e.g., in production)
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
