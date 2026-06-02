from typing import List
from fastapi import APIRouter, HTTPException, Header
from app.schemas.subscription_schema import SubscriptionResponse, ParticipantResponse
from app.services.subscription_service import SubscriptionService
from app.repositories.subscription_repository import SubscriptionRepository
from app.repositories.event_repository import EventRepository
from app.core.dependencies import get_current_user
from app.database import db

router = APIRouter()

subscription_repo = SubscriptionRepository(db)
event_repo = EventRepository(db)
subscription_service = SubscriptionService(subscription_repo, event_repo)


@router.post("/{event_id}/subscribe", response_model=dict)
def subscribe_event(event_id: str, x_user_id: str = Header(...)):
    """Subscribe user to an event."""
    current_user = get_current_user(x_user_id)
    return subscription_service.subscribe(event_id, current_user)


@router.delete("/{event_id}/unsubscribe", response_model=dict)
def unsubscribe_event(event_id: str, x_user_id: str = Header(...)):
    """Unsubscribe user from an event."""
    current_user = get_current_user(x_user_id)
    return subscription_service.unsubscribe(event_id, current_user)


@router.get("/{event_id}/participants", response_model=dict)
def get_participants(event_id: str):
    """Get list of participants for an event."""
    participants = subscription_service.get_participants(event_id)
    return {"participants": participants}
