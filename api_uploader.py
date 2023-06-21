        
from fastapi import  File, UploadFile, APIRouter, Form
import shutil

import uuid
import os

from typing import List, Optional
from function import uploading

router=APIRouter(tags=['Uploader'])

@router.post("/silverskillscre/ocr/uploader/")
# async def create_upload_file(doc: Optional[str] = Form(None),files: Optional[List[UploadFile]] = File(None)):
async def create_upload_file(files: Optional[List[UploadFile]] = File(None)):
   

   File_id=[]
   # if doc:
   #    file_id = str(uuid.uuid4())
   #    File_id.append(file_id)

   #    file_dir = os.path.dirname(doc)
   #    file_basename = os.path.basename(file_dir)
   #    root,ext = os.path.splitext(file_basename)
   #    file_name=os.path.join('.\\Server_data',str(file_id)+str(ext))

   #    with open(file_name, "r") as file:
   #          data=file.read()
   
   #    with open(file_name, "wb") as buffer:
   #       shutil.copyfileobj(data, buffer)
   #    return {"filename": file_basename,"file_id":File_id}

   if files:

      for file in files:
         file_id = str(uuid.uuid4())
         root,ext = os.path.splitext(str(file.filename))
         file_name=os.path.join('.\\Server_data',str(file_id)+str(ext))
         print(file_name)
         File_id.append(file_id)
         print(file.file)
         with open(file_name, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
      return {"filename": [file.filename for file in files],"file_id":[file for file in File_id]}
