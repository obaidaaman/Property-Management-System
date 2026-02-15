from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime, timezone
class Role(str, Enum):
    TENANT = "tenant"
    MANAGER = "manager"
    TECHNICIAN = "technician"

class TicketStatus(str, Enum):
    OPEN = "open"           
    ASSIGNED = "assigned"   
    IN_PROGRESS = "in_progress" 
    DONE = "done"           

class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# collection --> Properties
# class PropertyDB(BaseModel):
#     id: str
#     name: str             
#     address: str
#     manager_id: str        
#     unit_count: int        
#     created_at: datetime 

from src.utils.constants import Role

ALLOWED_TRANSITIONS = {
    "Open": ["Assigned"],
    "Assigned": ["In Progress"],
    "In Progress": ["Done"],
    "Done": [],
}

STATUS_ROLE_MAP = {
    "Assigned": Role.MANAGER,
    "In Progress": Role.TECHNICIAN,
    "Done": Role.TECHNICIAN,
}
