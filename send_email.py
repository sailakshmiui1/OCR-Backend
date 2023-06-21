import os
from fastapi_mail import FastMail, MessageSchema, MessageType
from pathlib import Path
from config import conf
from fastapi.responses import JSONResponse
from typing import List
from fastapi import APIRouter

# html = """
# <p>Please find the OTP</p> 
# """


async def reset_mail(subject:str, email_to:str,body:dict):
    message=MessageSchema(
        subject=subject,
        recipients=[email_to],
        template_body=body,
        subtype='html',
        # body=html,
        # subtype=MessageType.html
    )

    fm=FastMail(conf)
    await fm.send_message(message,template_name='sendmail.html')
    # await fm.send_message(message)




