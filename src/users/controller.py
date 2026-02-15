from fastapi import HTTPException
from firebase_admin import firestore
from src.utils.constants import Role
from .models import UserDetails
from google.cloud import firestore as ff
def get_all_users(current_user, db: firestore.client):
    try:
        if current_user.role is Role.MANAGER:
            user_query = db.collection("users").stream()
        else:
            doc_ref = db.collection("users").document(current_user.id)
            doc = doc_ref.get()
            if doc.exists:
                user_query [doc]
            else:
                return []
                
            

        user_list = []

        for doc in user_query:
            data = doc.to_dict()

            created_at = data.get("created_at")
            user_list.append(
                UserDetails(
                    id=doc.id,
                    email=data.get("email"),
                    full_name=data.get("full_name"),
                    role=data.get("role"),
                    block_name=data.get("block_name"),
                    unit_number=data.get("unit_number"),
                    phone_number=data.get("phone_number"),
                    property_id=data.get("property_id"),
                    is_active=data.get("is_active", True),
                    created_at=created_at,
                )
            )

        return user_list

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def update_user_profile(user_id: str, update_data: dict, db: firestore.Client):
    user_ref = db.collection("users").document(user_id)
    
   
    if not user_ref.get().exists:
        raise HTTPException(status_code=404, detail="User not found")

  
    allowed_updates = ["full_name", "phone_number", "block_name", "unit_number"]
    
    clean_data = {k: v for k, v in update_data.items() if k in allowed_updates}
    
    if not clean_data:
        raise HTTPException(status_code=400, detail="No valid fields to update")

    clean_data["updated_at"] = ff.SERVER_TIMESTAMP
    
    user_ref.update(clean_data)
    
    # Return the updated user
    updated_doc = user_ref.get().to_dict()
    return UserDetails(id=user_ref.id, **updated_doc)