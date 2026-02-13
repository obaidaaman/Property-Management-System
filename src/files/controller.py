import os
import shutil
import uuid
from typing import List
from fastapi import UploadFile

UPLOAD_DIR = "uploads"


def save_uploaded_files(files: List[UploadFile]) -> List[str]:
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    uploaded_urls = []

    for file in files:
        unique_name = f"{uuid.uuid4()}_{file.filename}"
        file_path = os.path.join(UPLOAD_DIR, unique_name)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        uploaded_urls.append(file_path)

    return {"image_urls": uploaded_urls}
