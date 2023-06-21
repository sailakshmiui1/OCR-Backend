import os

from dotenv import load_dotenv, dotenv_values

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pathlib import Path

load_dotenv(dotenv_path='.env')

class Settings():
    SECRET_KEY=os.getenv("SECRET_KEY")
    ALGORITHM=os.getenv("ALGORITHM")
   
settings=Settings()

config_cred=dotenv_values(".env")

conf=ConnectionConfig(
    MAIL_USERNAME = config_cred['MAIL_USERNAME'],
    MAIL_PASSWORD = config_cred['MAIL_PASSWORD'],
    MAIL_FROM = config_cred['MAIL_FROM'],
    MAIL_PORT= config_cred['MAIL_PORT'],
    MAIL_SERVER = config_cred['MAIL_SERVER'],
    MAIL_FROM_NAME = 'silverskillsdigital',
    MAIL_STARTTLS = False,
    MAIL_SSL_TLS = True,
    # TEMPLATE_FOLDER=Path(__file__).parent /'htmldirectory'
    TEMPLATE_FOLDER='htmldirectory'
)


