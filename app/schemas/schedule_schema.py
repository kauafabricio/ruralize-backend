from typing import Optional
from pydantic import BaseModel
from datetime import datetime


class ScheduleResponse(BaseModel):
    """User's confirmed event subscription with enriched event data"""
    id: str
    event_id: str
    user_id: str
    status: str
    created_at: datetime
    # Enriched event data
    event_title: Optional[str] = None
    event_description: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    points: Optional[int] = None
    promoter_name: Optional[str] = None
    promoter_photo: Optional[str] = None
    action_name: Optional[str] = None
    participant_count: Optional[int] = None


class ScheduleListResponse(BaseModel):
    """List of user's schedules with pagination"""
    schedules: list[ScheduleResponse]
    total: int
