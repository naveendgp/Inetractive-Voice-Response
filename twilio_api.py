import os
from flask import Flask, request
from twilio.twiml.voice_response import VoiceResponse, Gather
from twilio.twiml.messaging_response import MessagingResponse
from groq import Groq  # Import Groq package

# Set up Groq API key
groq_api_key ="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"

# Initialize Groq client
client = Groq(
    api_key=groq_api_key,
)

app = Flask(__name__)

def get_groq_response(prompt):
    """Groq Chat Completion"""
    try:
        # Call Groq API to generate a response
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model="llama3-8b-8192",  # Example of model, adjust based on the Groq model you are using
            stream=False,
        )
        return chat_completion.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error: {e}")
        return "Sorry, I couldn't process that request."

@app.route("/voice", methods=['POST'])
def answer_call():
    """Respond to voice inputs using Groq"""
    resp = VoiceResponse()

    if 'SpeechResult' in request.values:
        # Get the text transcription of what the caller said
        input_text = request.values['SpeechResult']
        print(f"SpeechResult: {input_text}")

        # Get response from Groq
        chat_response = get_groq_response(input_text)
        print('Groq Response:', chat_response)

        # Respond back with Groq's response
        resp.say(chat_response)
    else:
        # First response or no transcription available
        resp.say("Hey welcome to fam2bag, e-commerce. I'm an AI voice assistant, how can I help you?", voice='alice')

    # Collect further speech input
    gather = Gather(input='speech', action='/voice', speech_timeout='auto', hints="hello,buy,sell,order,product names,help")
    resp.append(gather)

    # If no input was received within the timeout, end the call
    resp.say("Time to go Bye-Bye")
    return str(resp)

@app.route("/sms", methods=['POST'])
def answer_sms():
    """Respond to SMS messages using Groq"""
    try:
        incoming_msg = request.form['Body']
        print('Incoming SMS:', incoming_msg)

        chat_response = get_groq_response(incoming_msg)
        print('SMS Groq Response:', chat_response)

        resp = MessagingResponse()

        # Add a text message (SMS)
        msg = resp.message(chat_response)

        return str(resp)
    except Exception as e:
        print('ERROR:', e)
        return str(MessagingResponse())

if __name__ == "__main__":
    app.run(debug=True)
