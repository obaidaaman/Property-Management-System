from src.auth.controller import  is_authenticated
from fastapi import APIRouter, Depends, status
from src.auth.controller import is_authenticated

user_route = APIRouter(prefix="/users")

@user_route.post("/edit-user")
def edit_user(current_user = Depends(is_authenticated)):
    pass
    

