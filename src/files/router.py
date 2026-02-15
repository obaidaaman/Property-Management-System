from fastapi import APIRouter, UploadFile, File
from typing import List
from .controller import save_uploaded_files
files_router = APIRouter(prefix="/files", tags=["Files"])



@files_router.post("/upload")
async def upload_files(files: List[UploadFile] = File(...)):
    if not files:
        return {"image_urls" : []}
    return save_uploaded_files(files)
   