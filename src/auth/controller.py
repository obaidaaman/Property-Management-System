from dotenv import load_dotenv
from firebase_admin import firestore
from datetime import datetime, timezone, timedelta
from fastapi import HTTPException, status, Request, Depends
from src.utils.db import get_db
from google.cloud import firestore as ff
from pwdlib import PasswordHash
from dotenv import load_dotenv
import jwt
import os
from .models import UserDB, UserResponse, LoginModel
from src.utils.constants import Role

load_dotenv()

password_hash = PasswordHash.recommended()

def get_password_hash(password:str) -> str:
    return password_hash.hash(password)


def verify_password(plain_password: str, hashed_password:str) -> str:
    return password_hash.verify(plain_password,hashed_password)



def create_auth(auth:UserDB, db : firestore.client, allow_manager_registration : bool = False):
    # Username validation
    # email validation
    # Then continue to create the user in the database

    if auth.role in [Role.MANAGER, Role.TECHNICIAN] and not allow_manager_registration:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot self-register as manager or technician. Contact administrator."
        )
    if auth.role == Role.TENANT:
        if not auth.block_name or not auth.unit_number:
            raise HTTPException(400, "Tenants must provide Block and Unit Number")
    user_collection = db.collection("users")

    existing_user = (
        user_collection.where("phone_number", "==", auth.phone_number)
        .limit(1)
        .stream()
    )
    
    if any(existing_user):
        raise HTTPException(400, detail="Phone number already exists")
    else:
        existing_email = (
        user_collection.where("email", "==", auth.email)
        .limit(1)
        .stream())
        if any(existing_email):
            raise HTTPException(400, detail="Email already exists")
    doc_ref = user_collection.document()
    hashed_password = get_password_hash(auth.password)
    doc_ref.set({
        "full_name" : auth.full_name,
        "password" : hashed_password,
        "email" : auth.email,
        "phone_number": auth.phone_number,
        "created_at": ff.SERVER_TIMESTAMP,
        "is_active" : True,
        "role" : auth.role,
        "block_name" : auth.block_name,
        "unit_number" : auth.unit_number
        
    })
    return UserResponse(
        id=doc_ref.id,
        email=auth.email,
        full_name=auth.full_name,
        role=auth.role,
        

    )


def login_user(auth : LoginModel, db : firestore.client):
    user_collection = db.collection("users")
    user_query = (user_collection.where("email", "==", auth.email).limit(1).stream())
    user_doc = list(user_query)
    
    if not user_doc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    
    user_data = user_doc[0].to_dict()
    
    if not verify_password(auth.password, user_data["password"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    
    # Generate JWT token
    token_data = {
        "user_id": user_doc[0].id,
        "email": user_data["email"],
        "role": user_data.get("role", None),
        "exp": datetime.now(timezone.utc) + timedelta(hours=24)  # Token expires in 24 hours
    }
    token = jwt.encode(token_data, os.getenv("SECRET_KEY"), algorithm=os.getenv("ALGORITHM"))
    
    return UserResponse(
        email=auth.email,
        full_name= user_data["full_name"],
        id= user_doc[0].id,
        role=user_data["role"],
        access_token=token,
        

    )


def is_authenticated(request: Request, db = Depends(get_db)):
    token = request.headers.get("authorization")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization Header Missing")
    token = token.split(" ")[-1]
    try :
        data = jwt.decode(token, os.getenv("SECRET_KEY"), algorithms=[os.getenv("ALGORITHM")])
    
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token ")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Authentication failed"
        )
    if not data:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization Header Missing")
    id = data.get("user_id")
    if not id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid token payload"
        )
    user = db.collection("users").document(id).get()
    if user.exists:
        user_data = user.to_dict()
        return UserResponse(id=user.id, email=user_data["email"], full_name=user_data["full_name"], role=user_data.get("role", None), unit_number=user_data.get("unit_number",""), block_number=user_data.get("block_number", ""))
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not Found")
