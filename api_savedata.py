from fastapi import  APIRouter

import os

router=APIRouter(tags=['OCR'])

@router.post("/silverskillscre/ocr/digitalizationScreen")
async def save_data(output_type: str):
    return{"message":"done"}