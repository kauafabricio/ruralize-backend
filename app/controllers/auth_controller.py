from fastapi import APIRouter
from app.schemas.user_schema import UserCreate, UserLogin
from app.services.auth_service import AuthService
from app.repositories.user_repository import UserRepository
from app.database import db

router = APIRouter()

# instâncias
user_repo = UserRepository(db)
auth_service = AuthService(user_repo)

# rota de cadastro
@router.post("/register")
def register(user: UserCreate):
    return auth_service.register(user)

# login
@router.post("/login")
def login(user: UserLogin):
    return auth_service.login(user)