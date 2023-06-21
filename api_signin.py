import os
import tokens
import hashing
from fastapi import APIRouter,Request, Response, Form, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse
from db import collection
from datetime import timedelta

router=APIRouter(tags=['Signin'])

@router.post('/silverskillscre/ocr/signin')
async def create_User(email: str=Form(...), password: str=Form(...)):
    errors=[]
    if not email:
        errors.append("Please valid email")
    
    user = collection.find_one({'email': email.lower()})
    
    if user is None:
        errors.append("Email does not exists")
        return {"Errors":errors[0]}
    elif user["active_status"]=="inactive":
        errors.append("User account is inactive. Please contact admin.")
        return {"Erros":errors[0]} 
    
    try:
        if hashing.Hash.verified(password,user['password']):
            jwt_token=tokens.create_access_token(data={"sub":email},expire_delta=timedelta(minutes=5))
            return {"jwt_token":jwt_token}
        else:
            errors.append("Invalid Password!")
            return {"errors":errors[0]}
    except:
        errors.append("Something went wrong!")
        return {"errors":errors[0]}
        