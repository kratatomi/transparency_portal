from threading import Thread
from flask import render_template
from flask_mail import Message
from app import app, mail

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email, args=(app, msg)).start()

def send_new_proposal_email(proposal):
    send_email('New proposal submitted',
               sender=app.config['ADMINS'][0],
               recipients=[app.config['ADMINS'][0]],
               text_body=render_template('email/new_proposal.txt', proposal=proposal),
               html_body=render_template('email/new_proposal.html', proposal=proposal))