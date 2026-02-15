from src.auth.controller import  is_authenticated
from fastapi import APIRouter, Depends, status
from typing import List, Optional
from src.tickets.controller import create_ticket, update_ticket, get_all_tickets, assignTicket, get_ticket_activity
from .models import TicketCreateRequest, TicketResponseModel, UpdateTicketStatusRequest, AssignTicketModel, ActivityLogModel
from src.utils.db import get_db



ticket_route = APIRouter(prefix="/ticket",tags=["Tickets"])


@ticket_route.post("/create-ticket", status_code=status.HTTP_201_CREATED, response_model=TicketResponseModel)
def create_user_ticket(ticket : TicketCreateRequest,current_user = Depends(is_authenticated), db =Depends(get_db)):
    return create_ticket(ticket=ticket,db=db,block_name=current_user.block_number, unit_number=current_user.unit_number,user_id=current_user.id)
    

@ticket_route.patch("/update-ticket/{ticket_id}", response_model=TicketResponseModel)
def update_user_ticket(
    ticket_id: str, 
    ticket_update: UpdateTicketStatusRequest, 
    current_user = Depends(is_authenticated),
    db = Depends(get_db)
):
    # exclude_unset=True removes any fields that were not in the request body
    clean_data = ticket_update.model_dump(exclude_unset=True)

    return update_ticket(
        ticket_id=ticket_id, 
        update_data=clean_data, 
        db=db, 
        current_user = current_user
    )
# List of all Tickets for Manager and list of tickets of users both with same api response based on the role.
@ticket_route.get("/get-tickets", status_code=status.HTTP_200_OK, response_model=List[TicketResponseModel],description="List all tickets or list tickets based on the current logged in user[Handles Tenant Manager and Technician also]")
def list_tickets(status: Optional[str] = None, priority: Optional[str] = None, target_user_id: Optional[str] = None,current_user = Depends(is_authenticated), db = Depends(get_db)):
    return get_all_tickets(user_id=current_user.id, db=db, role=current_user.role,target_user_id=target_user_id, status=status,priority=priority,)




# Assigning ticket to the technician
@ticket_route.post("/assign-tickets", status_code=status.HTTP_200_OK, response_model=TicketResponseModel,description="Assign ticket to the technician")
def assign_tickets(assignedTicket : AssignTicketModel,current_user = Depends(is_authenticated), db = Depends(get_db)):
    return assignTicket(ticket_id=assignedTicket.ticket_id,technician_id=assignedTicket.technician_id, db=db, role=current_user.role, current_user= current_user, comment=assignedTicket.comment)



@ticket_route.get("/{ticket_id}/activity", response_model=List[ActivityLogModel])
def get_activity_logs(
    ticket_id: str, 
    current_user = Depends(is_authenticated), 
    db = Depends(get_db)
):
    
    return get_ticket_activity(ticket_id, db)