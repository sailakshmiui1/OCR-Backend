from fastapi import APIRouter, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

import datetime
from db import collection
from hashing import Hash
from support import validate_password

router=APIRouter(tags=['Signup'])



@router.post('/silverskillscre/ocr/signup')
async def create_User(name: str=Form(...),email:str=Form(...), password:str=Form()):
    user = collection.find_one({'email': email.lower()})
    errors=[]
    if user:
        errors.append('Account already exist')
        return {"errors":errors[0]}
    passwd=validate_password(password)
    if passwd:
        errors.append(passwd)
        return {"errors":errors[0]}
    password = Hash.bcrypt(password)
    name=name.upper()
    email=email.lower()
    dt_string = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    data={"name":name,'email':email,'password':password,'created_date':dt_string, "status": "active"}
    collection.insert_one(data)
    return {"inserted":True}
