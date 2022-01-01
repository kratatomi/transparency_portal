from app import app
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import mail_settings

def send_new_proposal_email(proposal):
    from_addr = app.config['ADMINS'][0]
    to_addr = app.config['ADMINS'][0]
    text = f'Proposal ID {proposal.id} submitted'

    username = mail_settings.MAIL_USERNAME
    password = mail_settings.MAIL_PASSWORD

    msg = MIMEMultipart()

    msg['From'] = from_addr
    msg['To'] = to_addr
    msg['Subject'] = 'New proposal submitted'
    msg.attach(MIMEText(text))


    server = smtplib.SMTP(mail_settings.MAIL_SERVER, mail_settings.MAIL_PORT)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(username, password)
    server.sendmail(from_addr, to_addr, msg.as_string())
    server.quit()