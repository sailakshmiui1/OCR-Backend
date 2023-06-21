from fastapi import  APIRouter

import os

router=APIRouter(tags=['OCR'])

@router.post("/silverskillscre/ocr/ocr")
async def ocr(output_type: str,file_location:str):
    return{"message":"done"}
