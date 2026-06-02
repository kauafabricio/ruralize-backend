from typing import Optional
from pydantic import BaseModel
from datetime import datetime


class SubscriptionCreate(BaseModel):
    event_id: str


class SubscriptionUpdate(BaseModel):
    status: str


class SubscriptionResponse(BaseModel):
    id: str
    user_id: str
    event_id: str
    status: str
    created_at: datetime


class ParticipantResponse(BaseModel):
    user_id: str
    status: str
