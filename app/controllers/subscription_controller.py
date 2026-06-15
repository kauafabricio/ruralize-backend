from typing import List, Optional
from fastapi import APIRouter, HTTPException, Header
from app.repositories.event_repository import EventRepository
from app.schemas.subscription_schema import (
    SubscriptionResponse,
    SubscriptionListResponse,
    SubscriptionUpdate,
    UserSubscriptionResponse,
    ParticipantResponse,
)
from app.services.subscription_service import SubscriptionService
from app.repositories.subscription_repository import SubscriptionRepository
from app.repositories.points_repository import PointsRepository
from app.core.dependencies import get_current_user
from app.database import db

router = APIRouter()

subscription_repo = SubscriptionRepository(db)
event_repo = EventRepository(db)
points_repo = PointsRepository(db)
subscription_service = SubscriptionService(subscription_repo, event_repo, points_repo)

@router.get("/subscriptions", response_model=List[UserSubscriptionResponse])
def get_subscriptions(x_user_id: str = Header(...)):
    """List subscriptions from an user."""
    current_user = get_current_user(x_user_id)
    return subscription_service.get_subscriptions_by_user(current_user)

@router.get("/{event_id}/participants/me", response_model=Optional[ParticipantResponse])
def get_my_participation(event_id: str, x_user_id: str = Header(...)):
    """Get current user's subscription status for a specific event."""
    current_user = get_current_user(x_user_id)
    subscription = subscription_service.get_subscription_for_user_event(event_id, current_user)
    return {
        "user_id": subscription["user_id"],
        "status": subscription["status"],
    } if subscription else None


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

@router.patch("/{event_id}/participants/{participant_user_id}/status", response_model=dict)
def update_participant_status(
    event_id: str,
    participant_user_id: str,
    status_data: SubscriptionUpdate,
    x_user_id: str = Header(...),
):
    """Update attendance status for a participant."""
    current_user = get_current_user(x_user_id)
    return subscription_service.update_subscription_status(
        event_id,
        current_user,
        participant_user_id,
        status_data,
    )
