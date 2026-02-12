from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from src.utils.constants import Role

class LoginModel(BaseModel):
    email: str
    password: str         
    



class UserDB(BaseModel):
    email: str
    full_name: str
    password: str
    role: Role          
    phone_number: str
    property_id: Optional[str] = None 
    is_active: bool = True
    created_at: datetime 


class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    role: Role | None = None
    property_id: Optional[str] = None,
    access_token :Optional[str] = None