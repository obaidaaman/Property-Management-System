from fastapi import APIRouter, Depends, status, Request

from .models import UserDB, UserResponse, LoginModel
from .controller import create_auth, login_user as lu, is_authenticated
from src.utils.db import get_db
auth_router = APIRouter(prefix="/auth")


@auth_router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def signup_user(user: UserDB, db = Depends(get_db)):
    return create_auth(user, db)

@auth_router.post("/login", response_model=UserResponse, status_code=status.HTTP_200_OK)
def login_user(user: LoginModel, db = Depends(get_db)):
    return lu(user, db)


@auth_router.get("/is-authenticated", status_code=status.HTTP_200_OK, response_model=UserResponse)
def is_authenticated_user(request: Request, db = Depends(get_db)):
    return is_authenticated(request, db)