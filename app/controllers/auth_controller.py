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

# verificar status de conclusão de perfil
@router.get("/profile-completion-status/{user_id}")
def get_profile_completion_status(user_id: str):
    return auth_service.get_missing_profile_fields(user_id)