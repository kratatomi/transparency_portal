from app import app
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_new_proposal_email(proposal):
    from_addr = app.config['ADMINS'][0]
    to_addr = app.config['ADMINS'][0]
    text = f'Proposal ID {proposal.id} submitted'

    username = app.config["MAIL_USERNAME"]
    password = app.config["MAIL_PASSWORD"]

    msg = MIMEMultipart()

    msg['From'] = from_addr
    msg['To'] = to_addr
    msg['Subject'] = 'New proposal submitted'
    msg.attach(MIMEText(text))


    server = smtplib.SMTP(app.config['MAIL_SERVER'], app.config['MAIL_PORT'])
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(username, password)
    server.sendmail(from_addr, to_addr, msg.as_string())
    server.quit()