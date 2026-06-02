from typing import Optional
from pydantic import BaseModel


class ActionCreate(BaseModel):
    name: str
    description: str


class ActionUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class ActionResponse(BaseModel):
    id: str
    name: str
    description: str
