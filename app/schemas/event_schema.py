from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime


class EventCreate(BaseModel):
    title: str
    description: str
    action_id: str
    start_date: datetime
    end_date: datetime
    location_name: str
    address: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    max_participants: int
    points: int
    photo_url: Optional[str] = None
    status: str = "draft"


class EventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    action_id: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    location_name: Optional[str] = None
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    max_participants: Optional[int] = None
    points: Optional[int] = None
    photo_url: Optional[str] = None
    status: Optional[str] = None


class EventResponse(BaseModel):
    id: str
    title: str
    description: str
    promoter_id: str
    promoter_name: Optional[str] = None
    promoter_photo: Optional[str] = None
    action_id: str
    action_name: Optional[str] = None
    start_date: datetime
    end_date: datetime
    location_name: str
    address: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    max_participants: int
    points: int
    status: str
    photo_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    participant_count: int = 0


class EventListResponse(BaseModel):
    id: str
    title: str
    description: str
    promoter_name: Optional[str] = None
    action_name: Optional[str] = None
    start_date: datetime
    end_date: datetime
    location_name: str
    max_participants: int
    points: int
    status: str
    photo_url: Optional[str] = None
    participant_count: int = 0
