import logging
from fastapi import APIRouter, HTTPException, Header, Depends
from app.schemas.reward_schema import (
    RewardCreate,
    RewardUpdate,
    RewardResponse,
    RewardRedemptionDetail,
    RewardRedemptionRequest,
)
from app.services.reward_service import RewardService
from app.repositories.reward_repository import RewardRepository
from app.repositories.points_repository import PointsRepository
from app.repositories.user_repository import UserRepository
from app.core.dependencies import get_current_user
from app.database import db

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize repositories and services
reward_repo = RewardRepository(db)
points_repo = PointsRepository(db)
user_repo = UserRepository(db)
reward_service = RewardService(reward_repo, points_repo, user_repo)


@router.post("/admin/create", response_model=dict)
def create_reward(reward_data: RewardCreate):
    """Create a new reward (Admin only)"""
    try:
        reward_id = reward_repo.create_reward(reward_data.dict())
        return {
            "success": True,
            "message": "Recompensa criada com sucesso",
            "reward_id": reward_id
        }
    except Exception as e:
        logger.error(f"Error creating reward: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=list[RewardResponse])
def list_rewards():
    """Get all available rewards"""
    try:
        rewards = reward_repo.get_all_rewards()
        return rewards
    except Exception as e:
        logger.error(f"Error listing rewards: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/list", response_model=list[RewardResponse])
def list_rewards_alias():
    """Alias for compatibility with /rewards/list"""
    return list_rewards()


@router.get("/category/{category}", response_model=dict)
def get_rewards_by_category(category: str):
    """Get rewards by category"""
    try:
        rewards = reward_repo.get_rewards_by_category(category)
        return {
            "success": True,
            "data": rewards
        }
    except Exception as e:
        logger.error(f"Error fetching rewards by category: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{reward_id}", response_model=dict)
def get_reward_details(reward_id: str):
    """Get details of a specific reward"""
    try:
        reward = reward_repo.get_reward_by_id(reward_id)
        if not reward:
            raise HTTPException(status_code=404, detail="Recompensa não encontrada")

        return {
            "success": True,
            "data": reward
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching reward details: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{reward_id}", response_model=dict)
def update_reward(reward_id: str, reward_data: RewardUpdate):
    """Update a reward (Admin only)"""
    try:
        updated = reward_repo.update_reward(reward_id, reward_data.dict(exclude_unset=True))
        if not updated:
            raise HTTPException(status_code=404, detail="Recompensa não encontrada")

        return {
            "success": True,
            "message": "Recompensa atualizada com sucesso"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating reward: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{reward_id}", response_model=dict)
def delete_reward(reward_id: str):
    """Delete a reward (Admin only)"""
    try:
        reward_repo.delete_reward(reward_id)
        return {
            "success": True,
            "message": "Recompensa deletada com sucesso"
        }
    except Exception as e:
        logger.error(f"Error deleting reward: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/redeem", response_model=dict)
def redeem_reward(request: RewardRedemptionRequest, x_user_id: str = Header(...)):
    """
    Redeem a reward

    Endpoint que processa o resgate de uma recompensa. O usuário deve estar autenticado.

    Request headers:
        x_user_id: ID do usuário autenticado

    Request body:
        reward_id: ID da recompensa a ser resgatada

    Returns:
        - success: boolean
        - message: mensagem informativa
        - data: detalhes do resgate (quando bem-sucedido)
        - error_code: código do erro (quando falho)
    """
    try:
        logger.info(f"Reward redemption request from user {x_user_id} for reward {request.reward_id}")

        # Validate current user
        current_user = get_current_user(x_user_id)

        # Process redemption
        result = reward_service.redeem_reward(x_user_id, request.reward_id)

        if not result.get("success"):
            status_code = 400
            if result.get("error_code") == "USER_NOT_FOUND":
                status_code = 404
            elif result.get("error_code") == "REWARD_NOT_FOUND":
                status_code = 404
            elif result.get("error_code") == "INSUFFICIENT_POINTS":
                status_code = 402  # Payment Required

            raise HTTPException(status_code=status_code, detail=result)

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in redeem_reward: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "message": "Erro ao processar resgate",
                "error_code": "INTERNAL_SERVER_ERROR"
            }
        )


@router.get("/user/redemptions", response_model=list[RewardRedemptionDetail])
def get_user_redemptions(x_user_id: str = Header(...)):
    """
    Get all redemptions for the authenticated user

    Returns all reward redemptions made by the user, ordered by date.
    """
    try:
        current_user = get_current_user(x_user_id)
        result = reward_service.get_user_redemptions(x_user_id)

        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result)

        return result.get("data", [])

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching user redemptions: {str(e)}")
        raise HTTPException(status_code=400, detail="Erro ao buscar resgates")


@router.get("/code/{redemption_code}", response_model=dict)
def get_redemption_by_code(redemption_code: str):
    """
    Get redemption details by code

    Returns the details of a specific redemption using its unique code.
    """
    try:
        result = reward_service.get_redemption_details(redemption_code)

        if not result.get("success"):
            raise HTTPException(status_code=404, detail=result)

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching redemption by code: {str(e)}")
        raise HTTPException(status_code=400, detail="Erro ao buscar resgate")


@router.post("/code/{redemption_code}/collect", response_model=dict)
def mark_redemption_collected(redemption_code: str):
    """
    Mark a redemption as collected

    Updates the status of a redemption to 'collected' when the user picks up the reward.
    """
    try:
        result = reward_service.mark_collected(redemption_code)

        if not result.get("success"):
            status_code = 400
            if result.get("error_code") == "CODE_NOT_FOUND":
                status_code = 404

            raise HTTPException(status_code=status_code, detail=result)

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error marking redemption as collected: {str(e)}")
        raise HTTPException(status_code=400, detail="Erro ao marcar recompensa como coletada")
