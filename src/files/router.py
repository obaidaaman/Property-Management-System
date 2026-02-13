from fastapi import APIRouter, UploadFile, File
from typing import List
from .controller import save_uploaded_files
files_router = APIRouter(prefix="/files", tags=["Files"])

UPLOAD_DIR = "uploads"


@files_router.post("/")
async def upload_files(files: List[UploadFile] = File(...)):
    return save_uploaded_files(files)
   