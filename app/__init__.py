from flask import Flask, session
from flask_bootstrap import Bootstrap
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from datetime import timedelta
import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
import os
import server_settings
from flask_apscheduler import APScheduler # pip install Flask-APScheduler
import watchdog
import json

app = Flask(__name__)
bootstrap = Bootstrap(app)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db, render_as_batch=True)
login = LoginManager(app)
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

@scheduler.task('interval', id='ETF_watchdog', seconds=10, misfire_grace_time=900)
def ETF_watchdog():
    with open('data/ETF_investors_transfers.json') as etf_investors_transfers_file:
        ETF_investors_transfers = json.load(etf_investors_transfers_file)
    if ETF_investors_transfers["running"] == True:
        watchdog.main()
@app.before_request
def before_request():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=30)

if not app.debug:
    if server_settings.MAIL_SERVER:
        auth = None
        if server_settings.MAIL_USERNAME or server_settings.MAIL_PASSWORD:
            auth = (server_settings.MAIL_USERNAME, server_settings.MAIL_PASSWORD)
        secure = None
        if server_settings.MAIL_USE_TLS:
            secure = ()
        mail_handler = SMTPHandler(
            mailhost=(server_settings.MAIL_SERVER, server_settings.MAIL_PORT),
            fromaddr=app.config['ADMINS'][0],
            toaddrs=app.config['ADMINS'][0], subject='Transparency Portal Failure',
            credentials=auth, secure=secure)
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/transparency_portal.log', maxBytes=10240,
                                       backupCount=100)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info('Transparency Portal')

from app import routes, models, errors