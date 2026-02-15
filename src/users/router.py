from src.auth.controller import  is_authenticated
from fastapi import APIRouter, Depends, status
from src.utils.db import get_db
from .controller import get_all_users, update_user_profile
from typing import List
from .models import UserDetails, UpdateProfileRequest
user_route = APIRouter(prefix="/users",tags=["Users"])

@user_route.get("/get-user",status_code=status.HTTP_200_OK,response_model=List[UserDetails],description="Get all user or single user based on role")
def get_user(current_user = Depends(is_authenticated), db= Depends(get_db)):
    return get_all_users(current_user=current_user,db=db)
    

@user_route.patch("/me", response_model=UserDetails)
def update_my_profile(
    profile_update: UpdateProfileRequest,
    current_user = Depends(is_authenticated),
    db = Depends(get_db)
):
    data = profile_update.model_dump(exclude_unset=True)
    return update_user_profile(user_id=current_user.id, update_data=data, db=db)
