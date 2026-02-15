from typing import List, Optional, Literal
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
    
    created_at: datetime
    updated_at: datetime


class TicketCreateRequest(BaseModel):
    title: str
    description: str
    priority: Priority
    # Firebase Storage used for image store, on my backend project DB
    image_urls: List[str] = []
  
    

# 2. Manager assigning a technician
class AssignTicketRequest(BaseModel):
    technician_id: str
    comment: str

class UpdateTicketStatusRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[Priority] = None
    status: Optional[TicketStatus] = None
    comment: Optional[str] = None
    assigned_to: Optional[str] = None


class TicketResponseModel(BaseModel):
    id : str
    title  : str
    description: str
    priority: Optional[str] = None
    images : List[str] = None
    status : Optional[str] = None
    


class AssignTicketModel(BaseModel):
    ticket_id: str
    technician_id: str
    comment: Optional[str] = None


class ActivityLogModel(BaseModel):
    id: str 
    ticket_id: str 
    user_id: str
    user_role: str 
    type: Literal["comment", "status_change", "assignment", "creation"] 
    content: str 
    created_at: datetime