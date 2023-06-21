from datetime import timedelta

from fastapi import APIRouter, FastAPI, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import random

import tokens
from db import collection
from send_email import reset_mail
from tokens import create_access_token

router=APIRouter(tags=['Reset_Password'])
templates = Jinja2Templates(directory="htmldirectory")

# @router.get('/v2/reset_password',response_class=HTMLResponse)
# def get_item(request: Request):
#     context={'request':request}
#     return templates.TemplateResponse("reset_password.html", context)

@router.post('/silverskillscre/ocr/signin/reset_password',status_code=202)
async def reset_password(email:str):
    user = collection.find_one({"email": email.lower()})
    # print(user)
    
    if user is not None:
        number = random.randint(1000,9999)

        await reset_mail("Password Reset", user["email"],
             {
                "title": "Password Reset",
                "name": user["name"],
                "OTP": number
            }
        )
        return {"msg": "Email has been sent with instructions to reset your password."}

    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Your details not found, invalid email address"
        )
