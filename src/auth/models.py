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
    block_name: Optional[str] = None
    unit_number: Optional[str] = None          
    phone_number: str
    property_id: Optional[str] = None 
    is_active: bool = True
    


class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    block_number : Optional[str] = None
    unit_number: Optional[str] = None
    role: Role | None = None
   
    access_token :Optional[str] = None