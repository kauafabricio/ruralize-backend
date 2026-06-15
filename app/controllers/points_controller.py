from fastapi import APIRouter, Header, HTTPException
from app.schemas.points_schema import PointsBalanceResponse
from app.repositories.points_repository import PointsRepository
from app.core.dependencies import get_current_user
from app.database import db

router = APIRouter()
points_repo = PointsRepository(db)

@router.get("/balance", response_model=PointsBalanceResponse)
def get_points_balance(x_user_id: str = Header(...)):
    """Return the authenticated user's current points balance."""
    current_user = get_current_user(x_user_id)
    balance = points_repo.get_user_balance(current_user["id"])
    if balance is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return balance
