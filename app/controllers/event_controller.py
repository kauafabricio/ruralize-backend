from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, Header
from app.schemas.event_schema import EventCreate, EventUpdate, EventResponse, EventListResponse
from app.services.event_service import EventService
from app.repositories.event_repository import EventRepository
from app.repositories.action_repository import ActionRepository
from app.repositories.profile_repository import ProfileRepository
from app.core.dependencies import get_current_user
from app.database import db

router = APIRouter()

event_repo = EventRepository(db)
action_repo = ActionRepository(db)
profile_repo = ProfileRepository(db)
event_service = EventService(event_repo, action_repo, profile_repo)


@router.get("/", response_model=List[EventListResponse])
def list_events(
    action_id: Optional[str] = None,
    status: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
):
    """List events with optional filters."""
    return event_service.get_events_by_filter(action_id, status, start_date, end_date)


@router.get("/{event_id}", response_model=EventResponse)
def get_event(event_id: str):
    """Get event details by ID."""
    return event_service.get_event(event_id)


@router.post("/", response_model=dict)
def create_event(event: EventCreate, x_user_id: str = Header(...)):
    """Create a new event (teacher only)."""
    current_user = get_current_user(x_user_id)
    return event_service.create_event(event, current_user)


@router.put("/{event_id}", response_model=dict)
def update_event(event_id: str, event: EventUpdate, x_user_id: str = Header(...)):
    """Update an event (only promoter can edit)."""
    current_user = get_current_user(x_user_id)
    return event_service.update_event(event_id, event, current_user)


@router.delete("/{event_id}", response_model=dict)
def delete_event(event_id: str, x_user_id: str = Header(...)):
    """Delete an event (only promoter can delete)."""
    current_user = get_current_user(x_user_id)
    return event_service.delete_event(event_id, current_user)
