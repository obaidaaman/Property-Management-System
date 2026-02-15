from pydantic import BaseModel
from datetime import datetime
from src.utils.constants import Role
from typing import Optional

class UserDetails(BaseModel):
    id:str
    email: str
    full_name: str
    role: Role
    block_name: Optional[str] = None
    unit_number: Optional[str] = None          
    phone_number: str
    property_id: Optional[str] = None 
    is_active: bool = True
    created_at: datetime
    
class UpdateProfileRequest(BaseModel):
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    block_name: Optional[str] = None   # Tenants only
    unit_number: Optional[str] = None