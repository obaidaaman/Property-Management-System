from src.auth.controller import  is_authenticated
from fastapi import APIRouter, Depends, status
from typing import List
from src.tickets.controller import create_ticket, update_ticket, get_all_tickets_by_id
from .models import TicketCreateRequest, TicketResponseModel, UpdateTicketStatusRequest
from src.utils.db import get_db
from fastapi import File, UploadFile, Form
import shutil
import os

user_route = APIRouter(prefix="/ticket")


@user_route.post("/create-ticket", status_code=status.HTTP_201_CREATED, response_model=TicketResponseModel)
def create_user_ticket(ticket : TicketCreateRequest,current_user = Depends(is_authenticated), db =Depends(get_db)):
    return create_ticket(ticket=ticket,db=db,block_name=current_user.block_number, unit_number=current_user.unit_number,user_id=current_user.id)
    

@user_route.patch("/update-ticket/{ticket_id}", response_model=TicketResponseModel)
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

@user_route.get("/get-tickets", status_code=status.HTTP_200_OK, response_model=List[TicketResponseModel])
def list_ticket_by_current_user(current_user = Depends(is_authenticated), db = Depends(get_db)):
    return get_all_tickets_by_id(user_id=current_user.id, db=db)


