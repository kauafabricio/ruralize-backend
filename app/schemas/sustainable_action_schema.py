from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class SustainableActionCreate(BaseModel):
    name: str
    icon: Optional[str] = "🌱"


class SustainableActionUpdate(BaseModel):
    name: Optional[str] = None
    icon: Optional[str] = None


class SustainableActionResponse(BaseModel):
    id: str
    name: str
    icon: str
    is_default: bool
    created_by: Optional[str] = None
    created_at: datetime
