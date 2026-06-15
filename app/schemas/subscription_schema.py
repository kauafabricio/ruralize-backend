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


class SubscriptionListResponse(BaseModel):
    id: str
    user_id: str
    event_id: str
    status: str
    created_at: datetime


class ParticipantResponse(BaseModel):
    user_id: str
    status: str

# Schema simplificado com o que o card de agendamento precisa
class EventMinResponse(BaseModel):
    id: str
    title: str
    description: str
    start_date: datetime
    location_name: str

class UserSubscriptionResponse(BaseModel):
    id: str # ID da inscrição
    status: str
    created_at: datetime
    event: EventMinResponse # Dados do evento acoplados aqui
