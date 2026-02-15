from fastapi import HTTPException
from google.cloud import firestore as ff
from firebase_admin import firestore
from typing import Optional
from src.utils.constants import Role, TicketStatus, ALLOWED_TRANSITIONS, STATUS_ROLE_MAP
from .models import TicketCreateRequest, TicketResponseModel, ActivityLogModel


def validate_status_transition(current_status, new_status, user_role):
    if new_status not in ALLOWED_TRANSITIONS.get(current_status, []):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid transition from {current_status} to {new_status}",
        )

    required_role = STATUS_ROLE_MAP.get(new_status)

    if required_role and user_role != required_role:
        raise HTTPException(
            status_code=403,
            detail=f"{user_role} cannot change status to {new_status}",
        )


def create_ticket(ticket: TicketCreateRequest, db: firestore.client, block_name: str, unit_number: str, user_id: str):
    user_doc = db.collection("users").document(user_id).get()

    if not user_doc.exists:
        raise HTTPException(status_code=401, detail="Unauthorized user")

    ticket_doc = db.collection("tickets").document()
    ticket_doc.set({
        "user_id": user_id,
        "title": ticket.title,
        "description": ticket.description,
        "priority": ticket.priority,
        "images": ticket.image_urls,
        "status": TicketStatus.OPEN,
        "created_at": ff.SERVER_TIMESTAMP,
        "updated_at": ff.SERVER_TIMESTAMP,
        "assigned_to": None,
        "block_name": block_name,
        "unit_number": unit_number
    })

    return TicketResponseModel(
        id=ticket_doc.id,
        title=ticket.title,
        description=ticket.description,
        images=ticket.image_urls
    )


def update_ticket(ticket_id: str, update_data: dict, db: firestore.Client, current_user):
    ticket_ref = db.collection("tickets").document(ticket_id)
    ticket_snapshot = ticket_ref.get()

    if not ticket_snapshot.exists:
        raise HTTPException(status_code=404, detail="Ticket not found")

    existing_data = ticket_snapshot.to_dict()

    is_owner = existing_data.get("user_id") == current_user.id
    user_role = getattr(current_user, "role", None)
    is_manager = user_role == Role.MANAGER
    is_technician = user_role == Role.TECHNICIAN

    if not (is_owner or is_manager or is_technician):
        raise HTTPException(status_code=403, detail="Not authorized")

    new_status = update_data.get("status")
    current_status = existing_data.get("status")

    if new_status:
        validate_status_transition(
            current_status=current_status,
            new_status=new_status,
            user_role=current_user.role
        )

        if is_owner and not is_manager:
            raise HTTPException(403, "Tenant cannot update ticket status")

        if is_technician:
            if existing_data.get("assigned_to") != current_user.id:
                raise HTTPException(403, "Technician not assigned to this ticket")

    batch = db.batch()
    new_comment = update_data.pop("comment", None)

    if new_comment:
        log_ref = ticket_ref.collection("activity_logs").document()
        batch.set(log_ref, {
            "type": "comment",
            "content": new_comment,
            "user_id": current_user.id,
            "user_role": current_user.role,
            "created_at": ff.SERVER_TIMESTAMP
        })

    if new_status and new_status != existing_data.get("status"):
        log_ref = ticket_ref.collection("activity_logs").document()
        batch.set(log_ref, {
            "type": "status_change",
            "content": f"Changed status from {existing_data.get('status')} to {new_status}",
            "user_id": current_user.id,
            "user_role": current_user.role,
            "created_at": ff.SERVER_TIMESTAMP
        })

    update_data["updated_at"] = ff.SERVER_TIMESTAMP
    update_data["updated_by"] = current_user.id
    batch.update(ticket_ref, update_data)
    batch.commit()

    final_data = {**existing_data, **update_data}

    return TicketResponseModel(
        id=ticket_snapshot.id,
        title=final_data.get("title"),
        description=final_data.get("description"),
        images=final_data.get("images", []),
        status=final_data.get("status"),
    )


def get_all_tickets(
    user_id: str,
    role: str,
    db: ff.Client,
    target_user_id: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
):
    tickets_ref = db.collection("tickets")

    if role == Role.TENANT:
        query = tickets_ref.where("user_id", "==", user_id)

    elif role == Role.MANAGER:
        query = tickets_ref

        if target_user_id:
            query = query.where("user_id", "==", target_user_id)

        if status:
            query = query.where("status", "==", status)

        if priority:
            query = query.where("priority", "==", priority)

    

    elif role == Role.TECHNICIAN:
        query = tickets_ref.where("assigned_to", "==", user_id)

    else:
        return []

    docs = query.stream()

    tickets_list = []
    for doc in docs:
        data = doc.to_dict()
        tickets_list.append(
            TicketResponseModel(
                id=doc.id,
                title=data.get("title"),
                description=data.get("description"),
                status=data.get("status"),
                priority=data.get("priority"),
                images=data.get("images", []),
            )
        )

    return tickets_list

def assignTicket(ticket_id: str, technician_id: str, db: firestore.Client, role: str, current_user, comment: str):
    if current_user.role != Role.MANAGER:
        raise HTTPException(status_code=403, detail="Not authorized to assign tickets")

    ticket_ref = db.collection("tickets").document(ticket_id)
    ticket_snapshot = ticket_ref.get()

    if not ticket_snapshot.exists:
        raise HTTPException(status_code=404, detail="Ticket does not exist")

    ticket_data = ticket_snapshot.to_dict()

    if ticket_data.get("status") != TicketStatus.OPEN:
        raise HTTPException(400, "Only Open tickets can be assigned")

    tech_doc = db.collection("users").document(technician_id).get()
    if not tech_doc.exists:
        raise HTTPException(404, "Technician not found")

    batch = db.batch()

    batch.update(ticket_ref, {
        "assigned_to": technician_id,
        "assigned_by": current_user.id,
        "updated_at": ff.SERVER_TIMESTAMP,
        "status": TicketStatus.ASSIGNED,
    })

    log_ref = ticket_ref.collection("activity_logs").document()
    batch.set(log_ref, {
        "type": "assignment",
        "content": f"Assigned to technician {technician_id}",
        "user_id": current_user.id,
        "user_role": current_user.role,
        "created_at": ff.SERVER_TIMESTAMP
    })

    if comment:
        comment_ref = ticket_ref.collection("activity_logs").document()
        batch.set(comment_ref, {
            "type": "comment",
            "content": comment,
            "user_id": current_user.id,
            "user_role": current_user.role,
            "created_at": ff.SERVER_TIMESTAMP
        })

    batch.commit()

    existing_data = ticket_snapshot.to_dict()

    return TicketResponseModel(
        id=ticket_ref.id,
        title=existing_data.get("title"),
        description=existing_data.get("description"),
        images=existing_data.get("images", []),
        status=TicketStatus.ASSIGNED
    )


def get_ticket_activity(ticket_id: str, db: firestore.Client):
    logs_ref = db.collection("tickets").document(ticket_id).collection("activity_logs")
    query = logs_ref.order_by("created_at", direction=ff.Query.ASCENDING).stream()

    activity_list = []
    for doc in query:
        data = doc.to_dict()

        created_at = data.get("created_at")
        if hasattr(created_at, "to_datetime"):
            created_at = created_at.to_datetime()

        activity_list.append(
            ActivityLogModel(
                id=doc.id,
                ticket_id=ticket_id,
                user_id=data.get("user_id"),
                user_role=data.get("user_role"),
                type=data.get("type"),
                content=data.get("content"),
                created_at=created_at
            )
        )

    return activity_list
