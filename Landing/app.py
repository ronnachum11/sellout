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
    company_kb_id = "d614a15a-4c62-4d03-861b-2ec7d82bbfe2" #set_up_kb(data['company_name'], '', [data['company_website']])
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
    # email_gen = EmailGenerator(
    #     num_iterations=0,
    #     initial_prompt="""
    #     You are an email-writing assistant that writes
    #     first-contact emails to potential clients.
    #     """,
    #     user_name=data['user_name'],
    #     company_name=data['company_name'],
    #     company_kb_id=company_kb_id,
    #     customer_company_name=customer_data[0]['company'],
    #     customer_name=customer_data[0]['name'],
    #     customer_url=[customer_data[0]['company_website']]
    # )
    time.sleep(45)

    msg = """Dear Ron,

I trust this message finds you well. I'm Vignav from OpenAI, an organization that holds trust, privacy, and data security at its core. We ensure that our clients maintain complete ownership and control of their data, and we strictly do not use customer data for training our models. 

We are well aware of Jane Street's sophisticated, research-driven approach to trading. Our aim is not to replace your existing methodologies, but rather to offer supplementary AI solutions.

Our primary offerings include:

1. ChatGPT Enterprise: This solution is designed for businesses like Jane Street, offering controls, deployment tools, and speed to enhance productivity. It ensures data security through encryption both at rest and in transit, aligning with privacy laws like GDPR. 

2. API Platform: This platform provides access to our powerful models like GPT-4 and GPT-3.5 Turbo. It enables fine-tuning of models for specific tasks using your custom data, ensuring the solutions are tailored to your needs. 

Please let us know a convenient time for you, and we can arrange a call or meeting.

Best Regards,

Vignav
OpenAI Team"""
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
    
    time.sleep(25)
    customer_reply = """Hi Vignav, thanks for reaching out! Wanted to ask more about ChatGPT enterprise security - as a quantitative trading firm dealing with a lot of sensitive financial information, we need to make sure that our data is secure. Have you been audited for compliance with data security standards?
    
    Would also love to discuss this more by phone - my number is 7043510608. 
    
    Look forward to chatting,
    Ron"""
    on_reply(customer_data[0], customer_reply)

    return jsonify(data)

def on_reply(customer, message):
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
