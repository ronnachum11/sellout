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

if os.path.exists("debug.env"):
    load_dotenv("debug.env")

app = Flask(__name__)
# app.secret_key = os.environ['SECRET_KEY']

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/start-ai", methods=['POST'])
def start_ai():
    data = request.get_json()

    print("Indexing Comany Data...")
    company_kb_id = set_up_kb(data['company_name'], '', [data['company_website']])
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

    msg = email_gen.generate()
    print("Email Drafts Complete")

    print("\n\n\nSending Emails")
    print(msg)
    print("Emails Sent")

    return jsonify(data)

def on_reply():
    print("\n\n\nReplying to Response...")
    print("Reply Sent")

def generate_twiml(text):
    return str('''<?xml version="1.0" encoding="UTF-8"?>
               <Response>
               <Gather input="speech" action="https://188f-24-23-158-128.ngrok-free.app/handle-input" method="POST" speechTimeout="auto">
               <Say>''' + text + '''</Say>
               </Gather>
               </Response>'''
)

def call_customer(company_name, customer_name, customer_phone):
    print("\n\n\nCalling Customer...")
    account_sid = 'ACfdda12c5b78e66cc13365fcce8818585'
    auth_token = '19627121e9b6024da63d5c86152904b5'

    # Initialize the Twilio Client
    client = Client(account_sid, auth_token)

    text_to_read = f"Hi {customer_name}, thanks for agreeing to talk to me about {company_name}'s offerings!"
    twiml = generate_twiml(text_to_read)

    call = client.calls.create(
        twiml=twiml,
        to='+17043510608',
        from_='+18552200409'
    )

    print("Call Complete")

if __name__ == '__main__':
    app.run(debug=True, port=5000)
