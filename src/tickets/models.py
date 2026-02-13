from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timezone
from src.utils.constants import Priority, TicketStatus
from fastapi import UploadFile, File
class ActivityLog(BaseModel):
    actor_id: str      
    actor_name: str    
    action: str        
    details: str       
    timestamp : datetime

# collection is "tickets"
class TicketDB(BaseModel):
    id: str
    title: str
    description: str
    images: List[str] = [] 
    priority: Priority = Priority.LOW
    status: TicketStatus = TicketStatus.OPEN
    
    
    created_by: str        
    # property_id: str       
    assigned_to: Optional[str] = None 
    
    
    history: List[ActivityLog] = []
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)



class TicketCreateRequest(BaseModel):
    title: str
    description: str
    priority: Priority
    # Images currently is being uploaded and stored in local host, production requires s3 or firebase storage
    image_urls: List[str] = []
  
    

# 2. Manager assigning a technician
class AssignTicketRequest(BaseModel):
    technician_id: str
    comment: str

class UpdateTicketStatusRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[Priority] = None
    image_urls: Optional[List[str]] = None
    status: Optional[TicketStatus] = None
    comment: Optional[str] = None
    assigned_to: str


class TicketResponseModel(BaseModel):
    id : str
    title  : str
    description: str
    priority: Optional[str] = None
    images : List[str]

