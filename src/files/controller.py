import os
import shutil
import uuid
from typing import List
from fastapi import UploadFile, HTTPException
from firebase_admin import storage
UPLOAD_DIR = "uploads"


# def save_uploaded_files(files: List[UploadFile]) -> List[str]:
#     os.makedirs(UPLOAD_DIR, exist_ok=True)

#     uploaded_urls = []

#     for file in files:
#         unique_name = f"{uuid.uuid4()}_{file.filename}"
#         file_path = os.path.join(UPLOAD_DIR, unique_name)

#         with open(file_path, "wb") as buffer:
#             shutil.copyfileobj(file.file, buffer)

#         uploaded_urls.append(file_path)

#     return {"image_urls": uploaded_urls}
def save_uploaded_files(files: List[UploadFile]) -> List[str]:
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    uploaded_urls = []
    try:
        bucket =storage.bucket()
    except Exception:
        raise HTTPException(status_code=500, detail="Firebase Storage not initialised")
    for file in files:
        file_extension = file.filename.split(".")[-1]
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        blob = bucket.blob(f"tickets/images/{unique_filename}")
        blob.upload_from_file(file.file,content_type=file.content_type)
        blob.make_public()

        uploaded_urls.append(blob.public_url)

    return {"image_urls": uploaded_urls}
