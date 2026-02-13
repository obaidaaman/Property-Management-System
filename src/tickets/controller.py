
from fastapi import HTTPException
from google.cloud import firestore as ff
from firebase_admin import firestore
from src.utils.constants import Role
from .models import TicketCreateRequest, TicketResponseModel
def create_ticket(ticket : TicketCreateRequest, db: firestore.client, block_name : str, unit_number : str, user_id : str):

    user_doc = db.collection("users").document(user_id).get()

    if not user_doc.exists:
        raise HTTPException(status_code=401, detail="Unauthorized user")
    ticket_doc = db.collection("tickets").document()
    ticket_doc.set({
        "user_id": user_id,
        "title" : ticket.title,
        "description" : ticket.description,
        "priority" : ticket.priority,
        "images" : ticket.image_urls,
        "status" : "Open",
        "created_at" : ff.SERVER_TIMESTAMP,
        "updated_at": ff.SERVER_TIMESTAMP,
        "assigned_to": None
    })

    return TicketResponseModel(id=ticket_doc.id,title=ticket.title, description=ticket.description, images=ticket.image_urls)
    
def update_ticket(ticket_id: str, update_data: dict,db : firestore.client, current_user):
    

    try:
        ticket_data =db.collection("tickets").document(ticket_id)
        ticket_snapshot = ticket_data.get()
        if not ticket_snapshot.exists:
            raise HTTPException(status_code=403,detail="Ticket not found")\
        
        existing_data = ticket_snapshot.to_dict()
        is_owner = existing_data.get("user_id") == current_user.id
    
    
        is_manager = current_user.role == Role.MANAGER
    
    
        is_technician = current_user.role == Role.TECHNICIAN
        if not (is_owner or is_manager or is_technician):
            raise HTTPException(status_code=403, detail="Not authorized to update this ticket")
        if not update_data:
            return TicketResponseModel(id=ticket_data.id, **existing_data)
        
        
        update_data["updated_at"] = ff.SERVER_TIMESTAMP
        ticket_data.update(update_data)

        final_data = {**existing_data, **update_data}

        print(final_data)

        return TicketResponseModel(
            id=ticket_snapshot.id,
            title=final_data.get("title"),
            description=final_data.get("description"),
            images=final_data.get("images", [])
        )
    except HTTPException as e:
        print(e)
        raise HTTPException(detail="Something went wrong", status_code=500)
    



def get_all_tickets_by_id(user_id: str, db: firestore.client):
    try:
        tickets_query = db.collection("tickets").where("user_id", "==", user_id).stream()
        if tickets_query is None:
            return []
        tickets_list = []

        for doc in tickets_query:
            data = doc.to_dict()
            tickets_list.append(TicketResponseModel(id=doc.id,title=data.get("title", ""),description=data.get("description", ""),priority=data.get("priority", ""),images=data.get("images", [])))

        
        return tickets_list
    
    except HTTPException:
        raise HTTPException(status_code=401, detail="No tickets found") 
