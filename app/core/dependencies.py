from fastapi import Header, HTTPException
from app.repositories.user_repository import UserRepository
from app.database import db


def get_current_user(x_user_id: str = Header(...)):
    """Extract and validate current user from X-User-Id header"""
    user_repo = UserRepository(db)
    user_doc = user_repo.find_by_id(x_user_id)

    if not user_doc:
        raise HTTPException(status_code=401, detail="User not found")

    # Convert MongoDB document to serializable format
    user = {
        "id": str(user_doc["_id"]),
        "name": user_doc.get("name"),
        "email": user_doc.get("email"),
        "role": user_doc.get("role"),
        "registration": user_doc.get("registration"),
        "course": user_doc.get("course"),
        "department": user_doc.get("department"),
        "campus_location": user_doc.get("campus_location"),
        "description": user_doc.get("description"),
        "profile_photo_url": user_doc.get("profile_photo_url"),
        "cover_photo_url": user_doc.get("cover_photo_url"),
        "tags": user_doc.get("tags", [])
    }

    return user
