from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime, timezone
class Role(str, Enum):
    TENANT = "tenant"
    MANAGER = "manager"
    TECHNICIAN = "technician"

class TicketStatus(str, Enum):
    OPEN = "OPEN"           
    ASSIGNED = "ASSIGNED"   
    IN_PROGRESS = "IN_PROGRESS" 
    DONE = "DONE"           

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
    "OPEN": ["ASSIGNED"],
    "ASSIGNED": ["IN_PROGRESS"],
    "IN_PROGRESS": ["DONE"],
    "DONE": [],
}
STATUS_ROLE_MAP = {
    "Assigned": Role.MANAGER,
    "In Progress": Role.TECHNICIAN,
    "Done": Role.TECHNICIAN,
}


TASK_ASSIGNED= """
        Hi {name},
        You have been assigned with a new task,
        Description : {task_description}
        Tenant name : {tenant_name}
        Phone number : {phone_number}
        Block Number : {block_name}
        Unit Number : {unit_name}

        Please report to the assigned destination.
"""

TECHNICIAN_ASSIGNED= """
        Hi {name},
        A Technician has been assigned on your {ticket_title} ticket,
        Technician Name : {technician_name}
        Phone Number : {phone_number}
        

        The assigned official will report at your destination soon.
"""