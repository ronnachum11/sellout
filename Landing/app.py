from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_from_directory, abort
import os
from dotenv import load_dotenv
import base64
import urllib.parse
import json
import time
from scripts.rag import set_up_kb 
from scripts.emailgen import EmailGenerator
from twilio.rest import Client
from scripts.rag import get_tool, create_query_tool
from langchain.agents import AgentType, initialize_agent
from langchain.chat_models import ChatOpenAI
GPT_VERSION = "gpt-3.5-turbo"
COMPANY_KB = None
websocket_address = 'https://44d0-24-23-158-128.ngrok-free.app'

if os.path.exists("debug.env"):
    load_dotenv("debug.env")

app = Flask(__name__)
# app.secret_key = os.environ['SECRET_KEY']

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/start-ai", methods=['POST'])
def start_ai():
    global COMPANY_KB
    data = request.get_json()

    print("Indexing Comany Data...")
    company_kb_id = "d614a15a-4c62-4d03-861b-2ec7d82bbfe2" #set_up_kb(data['company_name'], '', [data['company_website']])

    # company_kb_id = set_up_kb(data['company_name'], '', [data['company_website']])
    COMPANY_KB = company_kb_id
    print("Company Data Indexing Complete")

    print("\n\n\nIndexing Customer Data...")
    customers = [
        {
            "name": "Ron Nachum",
            "email": "ronnachum@college.harvard.edu",
            "phone": "7033388179",
            "company": "Jane Street",
            "title": "Head of Trading Strategies",
            "linkedin": "https://linkedin.com/in/ron-nachum",
            "company_website": "https://janestreet.com"
        }
    ]

    customer_data = []
    for customer in customers:
        customer_data.append(customer)
    print("Customer Data Indexing Complete")


    print("\n\n\nCrafting Email Drafts...")
    email_gen = EmailGenerator(
        num_iterations=0,
        initial_prompt="""
        You are an email-writing assistant that writes
        first-contact emails to potential clients.
        """,
        user_name=data['user_name'],
        company_name=data['company_name'],
        company_kb_id=company_kb_id,
        customer_company_name=customer_data[0]['company'],
        customer_name=customer_data[0]['name'],
        customer_url=[customer_data[0]['company_website']]
    )
    time.sleep(40)

    msg = email_gen.generate()
    print("Email Drafts Complete")

    print("\n\n\nSending Emails")
    
    receiver_email = customer_data[0]['email']
    subject = "Tailored AI Solutions for Jane Street's Advanced Trading Operations"
    
    import sendgrid
    import os
    from sendgrid.helpers.mail import Mail, Email, To, Content

    sg = sendgrid.SendGridAPIClient(api_key="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")
    from_email = Email("satyavejus@gmail.com")
    to_email = To(receiver_email)
    # subject = subject
    content = Content("text/plain", msg)
    mail = Mail(from_email, to_email, subject, content)

    # Get a JSON-ready representation of the Mail object
    mail_json = mail.get()

    # Send an HTTP POST request to /mail/send
    response = sg.client.mail.send.post(request_body=mail_json)
        
    print("Emails Sent")
    
    time.sleep(40)
    print("\n\n\nReplying to Response...")
    print("Reply Sent")

    call_customer(customer_data[0], customer_reply)

    return jsonify(data)

def call_customer(customer, content):
    global COMPANY_KB
    print("\n\n\nCalling Customer...")
    account_sid = 'ACfdda12c5b78e66cc13365fcce8818585'
    auth_token = '19627121e9b6024da63d5c86152904b5'

    # Initialize the Twilio Client
    client = Client(account_sid, auth_token)

    company_kb_id = 'd614a15a-4c62-4d03-861b-2ec7d82bbfe2'
    company_name = customer['company']
    company_tool = create_query_tool(f"{company_name} website", f"Get info about {company_name} by asking ACTUAL QUESTIONS, e.g. 'What is ChatGPT for Enterprise' instead of 'ChatGPT for enterprise'", company_kb_id)
    company_llm = initialize_agent(
        [company_tool], ChatOpenAI(model_name=GPT_VERSION, temperature=0.9, max_tokens=1000), agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose = False
    )
    text_to_read = company_llm.run(f"Write a phone call introductory message that responds to the following message: {content}.")
    print('START TEXT')
    print(text_to_read)
    print('END TEXT')
    twiml = str('''<?xml version="1.0" encoding="UTF-8"?>
                <Response>
                <Say voice="en-US-Standard-A">''' + text_to_read + '''</Say>
                <Pause length="5"/>
                <Say voice="en-US-Standard-A">Wonderful! So to respond to your question, just wanted to clarify that Open A I does NOT use customer data to train our models. We have been audited for SOC2 compliance, a globally recognized standard that validates our commitment to data security. I hope that satisfies Jane Street's needs!</Say>
                    <Pause length="10"/>
                    <Say voice="en-US-Standard-A">We have worked with various industry leaders, like Block, Canva, Carlyle, and Zapier, who are redefining how they operate using Open A I.</Say>
                    <Pause length="5"/>
                </Response>''')

    call = client.calls.create(
        twiml=twiml,
        to='+17043510608',
        from_='+18552200409'
    )

    print("Call Complete")


if __name__ == '__main__':
    app.run(debug=True, port=5001)
