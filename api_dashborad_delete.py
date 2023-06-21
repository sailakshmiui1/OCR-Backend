from fastapi import  APIRouter
import db

import os

router=APIRouter(tags=['Delete'])

@router.post("/silverskillscre/ocr/Dashboard/convertedDocument/{name}")
async def delete_from_database(fileid: str,filename:str):
    
    file=db.collection.find_one({'filename': filename})
    if file is None: 
        return {'Error':'File do not exist in the database.'}
    db.collection.delete_one({'fileid':fileid,'filename':filename})
    return {'message':'file has been deleted.'}
    