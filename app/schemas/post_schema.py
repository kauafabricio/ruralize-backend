from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class PostCreate(BaseModel):
    content: str
    location: Optional[str] = None
    sustainable_action: Optional[str] = Field(None, alias="sustainable_action_id")
    event_id: Optional[str] = None
    image_url: Optional[str] = None

    class Config:
        allow_population_by_field_name = True

class PostUpdate(BaseModel):
    content: Optional[str] = None
    location: Optional[str] = None
    sustainable_action: Optional[str] = Field(None, alias="sustainable_action_id")
    event_id: Optional[str] = None
    image_url: Optional[str] = None

    class Config:
        allow_population_by_field_name = True

class CommentCreate(BaseModel):
    user_id: str
    content: str

class Comment(BaseModel):
    user_id: str
    content: str
    created_at: datetime

class CommentWithUser(BaseModel):
    user_id: str
    user_name: str
    user_photo: Optional[str] = None
    content: str
    created_at: datetime

class UserLike(BaseModel):
    user_id: str
    user_name: str
    user_photo: Optional[str] = None

class PostResponse(BaseModel):
    id: str
    user_id: str
    content: str
    location: Optional[str]
    sustainable_action: Optional[str]
    sustainable_action_id: Optional[str] = None
    event_id: Optional[str]
    image_url: Optional[str]
    likes: int
    liked_by: List[UserLike]
    comments: List[CommentWithUser]
    user_name: Optional[str] = None
    user_photo: Optional[str] = None
    created_at: datetime

class PostEnrichedResponse(PostResponse):
    pass
