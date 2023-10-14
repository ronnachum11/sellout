from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_from_directory, abort
import os
from dotenv import load_dotenv
import base64
import urllib.parse
import json
import time
from scripts.rag import set_up_kb 

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
    id = set_up_kb(data['company_name'], '', [data['company_website']])
    print("Company Data Indexing Complete")

    print("\n\n\nIndexing Customer Data...")
    customers = [
        {
            "name": "Ron Nachum",
            "email": "ronnachum@college.harvard.edu",
            "company": "Jane Street",
            "title": "Head of Trading Strategies",
            "linkedin": "https://linkedin.com/in/ron-nachum"
        }
    ]

    for customer in customers:
        # PROCESS LINKEDIN
        customer_desires = [] # get_customer_info(customer['linkedin'])
    print("Customer Data Indexing Complete")

    print("\n\n\nCoalescing Company Offerings, Customer Needs...")

    print("Coalescing Complete")

    print("\n\n\nCrafting Email Drafts...")

    print("Email Drafts Complete")

    print("\n\n\nSending Emails")

    print("Emails Sent")

    return jsonify(data)

def on_reply(offer, customer):
    print("\n\n\nReplying to Response...")
    print("Reply Sent")

def call_customer(offer, customer):
    print("\n\n\nCalling Customer...")
    print("Call Complete")

if __name__ == '__main__':
    app.run(debug=True, port=5000)
