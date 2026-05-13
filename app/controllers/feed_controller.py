from fastapi import APIRouter
from app.services.feed_service import FeedService
from app.repositories.post_repository import PostRepository
from app.repositories.user_repository import UserRepository
from app.database import db

router = APIRouter()

post_repo = PostRepository(db)
user_repo = UserRepository(db)

feed_service = FeedService(post_repo, user_repo)

@router.get("/general")
def get_general_feed():
    return feed_service.get_general_feed()

@router.get("/friends/{user_id}")
def get_friends_feed(user_id: str):
    return feed_service.get_friends_feed(user_id)