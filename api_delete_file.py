from fastapi import  APIRouter

import os

router=APIRouter(tags=['Delete'])

@router.post("/silverskillscre/ocr/uploader/filelist")
async def delete_server_file(file_loc: str):
    if os.path.isfile(file_loc):
        os.remove(file_loc)
        return {"message": "File is deleted"}
    else:
        return { "message":"File do not exist"}

   