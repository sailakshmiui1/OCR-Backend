from fastapi import  APIRouter
import db

import os

router=APIRouter(tags=['Dashborad'])

@router.post("/silverskillscre/ocr/dashboard/userlist/")
async def user_activation_deactivation(emailid:str,status: str):
    if status=="active":
        db.collection.update_one({'email': emailid.lower()},{"$set":{"active_status":"active"}})
        return {'message':'User is active'}
    elif status=="inactive":
        db.collection.update_one({'email': emailid.lower()},{"$set":{"active_status":"inactive"}})
        return {'message':'User is inactive'}


