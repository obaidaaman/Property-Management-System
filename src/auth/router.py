from fastapi import APIRouter, Depends, status, Request, HTTPException
from src.utils.constants import Role
from .models import UserDB, UserResponse, LoginModel, StaffCreateRequest
from .controller import create_auth, login_user as lu, is_authenticated
from src.utils.db import get_db
auth_router = APIRouter(prefix="/auth",tags=["Authentication"])


@auth_router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def signup_user(user: UserDB, db = Depends(get_db)):
    return create_auth(user, db,)

# @auth_router.post("/register-technician", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
# def signup_technician(user: UserDB, db = Depends(get_db)):
#     return create_auth(user, db,allow_manager_registration=True)

@auth_router.post("/login", response_model=UserResponse, status_code=status.HTTP_200_OK)
def login_user(user: LoginModel, db = Depends(get_db)):
    return lu(user, db)


@auth_router.get("/is-authenticated", status_code=status.HTTP_200_OK, response_model=UserResponse)
def is_authenticated_user(request: Request, db = Depends(get_db)):
    return is_authenticated(request, db)





@auth_router.post("/create-staff", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_staff_user(
    user: StaffCreateRequest, 
    current_user = Depends(is_authenticated), 
    db = Depends(get_db)
):
  
    if current_user.role != Role.MANAGER:
        raise HTTPException(
            status_code=403, 
            detail="Only Managers can create staff accounts."
        )


    if user.role == Role.TENANT:
        raise HTTPException(status_code=400, detail="You are not allowed to create technician profile as a Tenant")


    return create_auth(auth=user, db=db, allow_manager_registration=True)