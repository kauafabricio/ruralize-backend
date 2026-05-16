from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class PostCreate(BaseModel):
    content: str
    location: Optional[str] = None
    sustainable_action: str
    event_id: Optional[str] = None
    image_url: Optional[str] = None

class PostUpdate(BaseModel):
    content: Optional[str] = None
    location: Optional[str] = None
    sustainable_action: Optional[str] = None
    event_id: Optional[str] = None
    image_url: Optional[str] = None

class CommentCreate(BaseModel):
    user_id: str
    content: str

class Comment(BaseModel):
    user_id: str
    content: str
    created_at: datetime

class PostResponse(BaseModel):
    id: str
    user_id: str
    content: str
    location: Optional[str]
    sustainable_action: str
    event_id: Optional[str]
    image_url: Optional[str]
    likes: int
    liked_by: List[str]
    comments: List[Comment]
    created_at: datetime