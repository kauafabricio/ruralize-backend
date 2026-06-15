import logging
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from pymongo.errors import DuplicateKeyError

from app.database import db

logger = logging.getLogger(__name__)


class RewardService:
    """Service for handling reward redemptions"""

    def __init__(self, reward_repository, points_repository, user_repository):
        """
        Initialize reward service with required repositories and services

        Args:
            reward_repository: RewardRepository instance
            points_repository: PointsRepository instance
            user_repository: UserRepository instance
        """
        self.reward_repo = reward_repository
        self.points_repo = points_repository
        self.user_repo = user_repository

    def generate_redemption_code(self, length: int = 8) -> str:
        """
        Generate a unique alphanumeric redemption code

        Args:
            length: Length of the code

        Returns:
            str: Unique redemption code
        """
        alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        return "".join(secrets.choice(alphabet) for _ in range(length))

    def _generate_unique_redemption_code(self, length: int = 8) -> str:
        """
        Generate a redemption code and ensure uniqueness in the database
        """
        for _ in range(10):
            code = self.generate_redemption_code(length)
            if not self.reward_repo.get_redemption_by_code(code):
                return code

        # Fallback to a safer token if collisions happen repeatedly
        return secrets.token_urlsafe(length).upper()[:length]

    def redeem_reward(self, user_id: str, reward_id: str) -> Dict[str, Any]:
        """
        Process a reward redemption

        Steps:
        1. Fetch user from database using userId
        2. Fetch reward from database using reward_id
        3. Validate user has sufficient points
        4. Generate unique redemption code
        5. Deduct points and record the redemption in database
        6. Return response to frontend

        Args:
            user_id: ID of the user redeeming the reward
            reward_id: ID of the reward to redeem

        Returns:
            Dict with redemption details or error message
        """
        try:
            # Step 1: Fetch user
            user = self.user_repo.find_by_id(user_id)
            if not user:
                logger.warning(f"User not found: {user_id}")
                return {
                    "success": False,
                    "message": "Usuário não encontrado",
                    "error_code": "USER_NOT_FOUND"
                }

            user_name = user.get("name")
            user_email = user.get("email")

            logger.info(f"Processing reward redemption for user {user_id} ({user_name})")

            # Step 2: Fetch reward
            reward = self.reward_repo.get_reward_by_id(reward_id)
            if not reward:
                logger.warning(f"Reward not found: {reward_id}")
                return {
                    "success": False,
                    "message": "Recompensa não encontrada",
                    "error_code": "REWARD_NOT_FOUND"
                }

            # Step 3: Validate points
            user_points = self.points_repo.get_user_balance(user_id)
            if not user_points:
                logger.warning(f"Could not fetch points for user {user_id}")
                return {
                    "success": False,
                    "message": "Erro ao verificar saldo de pontos",
                    "error_code": "POINTS_CHECK_ERROR"
                }

            current_balance = user_points.get("balance", 0)
            points_required = reward.get("points_required", 0)

            if current_balance < points_required:
                logger.warning(f"Insufficient points for user {user_id}. Required: {points_required}, Current: {current_balance}")
                return {
                    "success": False,
                    "message": f"Pontos insuficientes. Você tem {current_balance} pontos e precisa de {points_required}",
                    "error_code": "INSUFFICIENT_POINTS",
                    "current_balance": current_balance,
                    "points_required": points_required
                }

            # Step 4: Generate unique redemption code
            redemption_code = self._generate_unique_redemption_code()
            logger.info(f"Generated redemption code: {redemption_code}")

            pickup_deadline = datetime.utcnow() + timedelta(days=7)

            transaction_data = {
                "user_id": str(user_id),
                "amount": -points_required,
                "transaction_type": "reward_redemption",
                "description": f"Resgate de recompensa: {reward.get('name')}",
                "related_id": reward_id
            }

            redemption_data = {
                "user_id": user_id,
                "user_email": user_email,
                "user_name": user_name,
                "reward_id": reward_id,
                "reward_name": reward.get("name"),
                "points_deducted": points_required,
                "redemption_code": redemption_code,
                "pickup_deadline": pickup_deadline,
                "pickup_location": "Sala 24 - DC Sala Ruralize",
                "status": "pending",
                "redeemed_at": datetime.utcnow()
            }

            session = None
            try:
                session = db.client.start_session()
            except Exception as e:
                logger.warning(
                    f"MongoDB sessions not available, proceeding without transactions: {e}",
                )
                session = None

            try:
                if session is not None:
                    with session.start_transaction():
                        transaction_id = self.points_repo.create_transaction(transaction_data, session=session)
                        redemption_id = self.reward_repo.create_redemption(redemption_data, session=session)
                        self.reward_repo.increment_quantity_redeemed(reward_id, session=session)
                else:
                    transaction_id = self.points_repo.create_transaction(transaction_data)
                    redemption_id = self.reward_repo.create_redemption(redemption_data)
                    self.reward_repo.increment_quantity_redeemed(reward_id)

                logger.info(f"Points transaction created: {transaction_id}")
                logger.info(f"Redemption recorded: {redemption_id}")
            except DuplicateKeyError:
                logger.warning("Redemption code collision, retrying with a new code")
                redemption_code = self._generate_unique_redemption_code()
                redemption_data["redemption_code"] = redemption_code
                if session is not None:
                    with session.start_transaction():
                        transaction_id = self.points_repo.create_transaction(transaction_data, session=session)
                        redemption_id = self.reward_repo.create_redemption(redemption_data, session=session)
                        self.reward_repo.increment_quantity_redeemed(reward_id, session=session)
                else:
                    transaction_id = self.points_repo.create_transaction(transaction_data)
                    redemption_id = self.reward_repo.create_redemption(redemption_data)
                    self.reward_repo.increment_quantity_redeemed(reward_id)
            finally:
                if session is not None:
                    session.end_session()

            return {
                "success": True,
                "message": "Recompensa resgatada com sucesso! Seu código de retirada foi gerado.",
                "data": {
                    "redemption_id": redemption_id,
                    "user_id": user_id,
                    "reward_id": reward_id,
                    "reward_name": reward.get("name"),
                    "user_email": user_email,
                    "user_name": user_name,
                    "points_deducted": points_required,
                    "redemption_code": redemption_code,
                    "pickup_deadline": pickup_deadline.isoformat(),
                    "pickup_location": "Sala 24 - DC Sala Ruralize",
                    "status": "pending",
                    "redeemed_at": datetime.utcnow().isoformat()
                }
            }

        except Exception as e:
            logger.error(f"Unexpected error during reward redemption: {str(e)}", exc_info=True)
            return {
                "success": False,
                "message": "Erro inesperado ao processar resgate",
                "error_code": "INTERNAL_SERVER_ERROR"
            }

    def get_user_redemptions(self, user_id: str):
        """
        Get all redemptions for a user

        Args:
            user_id: ID of the user

        Returns:
            List of redemption records
        """
        try:
            redemptions = self.reward_repo.get_redemptions_by_user(user_id)
            return {
                "success": True,
                "data": redemptions
            }
        except Exception as e:
            logger.error(f"Error fetching redemptions for user {user_id}: {str(e)}")
            return {
                "success": False,
                "message": "Erro ao buscar resgates",
                "error_code": "FETCH_ERROR"
            }

    def get_redemption_details(self, redemption_code: str):
        """
        Get details of a specific redemption by its code

        Args:
            redemption_code: The unique redemption code

        Returns:
            Redemption details
        """
        try:
            redemption = self.reward_repo.get_redemption_by_code(redemption_code)
            if not redemption:
                return {
                    "success": False,
                    "message": "Código de resgate não encontrado",
                    "error_code": "CODE_NOT_FOUND"
                }

            return {
                "success": True,
                "data": redemption
            }
        except Exception as e:
            logger.error(f"Error fetching redemption details: {str(e)}")
            return {
                "success": False,
                "message": "Erro ao buscar detalhes do resgate",
                "error_code": "FETCH_ERROR"
            }

    def mark_collected(self, redemption_code: str):
        """
        Mark a redemption as collected (pickup completed)

        Args:
            redemption_code: The unique redemption code

        Returns:
            Success or error response
        """
        try:
            redemption = self.reward_repo.get_redemption_by_code(redemption_code)
            if not redemption:
                return {
                    "success": False,
                    "message": "Código de resgate não encontrado",
                    "error_code": "CODE_NOT_FOUND"
                }

            # Check if not already collected
            if redemption.get("status") == "collected":
                return {
                    "success": False,
                    "message": "Esta recompensa já foi coletada",
                    "error_code": "ALREADY_COLLECTED"
                }

            # Check if not expired
            pickup_deadline = redemption.get("pickup_deadline")
            if isinstance(pickup_deadline, str):
                from datetime import datetime as dt
                pickup_deadline = dt.fromisoformat(pickup_deadline.replace('Z', '+00:00'))

            if datetime.utcnow() > pickup_deadline:
                return {
                    "success": False,
                    "message": "Prazo para retirada expirou",
                    "error_code": "PICKUP_EXPIRED"
                }

            # Mark as collected
            self.reward_repo.mark_redemption_collected(redemption.get("id"))

            return {
                "success": True,
                "message": "Recompensa marcada como coletada",
                "data": redemption
            }

        except Exception as e:
            logger.error(f"Error marking redemption as collected: {str(e)}")
            return {
                "success": False,
                "message": "Erro ao marcar recompensa como coletada",
                "error_code": "UPDATE_ERROR"
            }
