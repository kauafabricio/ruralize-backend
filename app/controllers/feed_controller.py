from fastapi import APIRouter
from app.services.feed_service import FeedService
from app.repositories.post_repository import PostRepository
from app.repositories.user_repository import UserRepository
from app.repositories.profile_repository import ProfileRepository
from app.database import db

router = APIRouter()

post_repo = PostRepository(db)
user_repo = UserRepository(db)
profile_repo = ProfileRepository(db)

feed_service = FeedService(post_repo, user_repo, profile_repo)

@router.get("/")
def get_general_feed(user_id: str = None):
    return feed_service.get_general_feed(user_id)


# CONSIDERAR EM TIRAR ESSE GET

@router.get("/following/{user_id}")
def get_following_feed(user_id: str):
    return feed_service.get_following_feed(user_id)