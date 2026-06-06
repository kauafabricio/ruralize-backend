import logging
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class RewardService:
    """Service for handling reward redemptions"""

    def __init__(self, reward_repository, points_repository, user_repository, email_service):
        """
        Initialize reward service with required repositories and services

        Args:
            reward_repository: RewardRepository instance
            points_repository: PointsRepository instance
            user_repository: UserRepository instance
            email_service: EmailService instance
        """
        self.reward_repo = reward_repository
        self.points_repo = points_repository
        self.user_repo = user_repository
        self.email_service = email_service

    def generate_redemption_code(self, length: int = 8) -> str:
        """
        Generate a unique alphanumeric redemption code

        Args:
            length: Length of the code

        Returns:
            str: Unique redemption code
        """
        return secrets.token_hex(length // 2).upper()

    def redeem_reward(self, user_id: str, reward_id: str) -> Dict[str, Any]:
        """
        Process a reward redemption

        Steps:
        1. Fetch user from database using userId
        2. Fetch reward from database using reward_id
        3. Validate user has sufficient points
        4. Generate unique redemption code
        5. Send confirmation email
        6. Only deduct points after successful email send
        7. Record the redemption in database
        8. Return response to frontend

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

            if not user_email:
                logger.error(f"User {user_id} has no email registered")
                return {
                    "success": False,
                    "message": "Usuário não possui e-mail cadastrado",
                    "error_code": "NO_EMAIL_REGISTERED"
                }

            logger.info(f"Processing reward redemption for user {user_id} ({user_name} - {user_email})")

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
            redemption_code = self.generate_redemption_code()
            logger.info(f"Generated redemption code: {redemption_code}")

            # Step 5: Send confirmation email
            pickup_deadline = datetime.utcnow() + timedelta(days=7)

            email_sent = self.email_service.send_reward_redemption_email(
                recipient_email=user_email,
                user_name=user_name,
                reward_name=reward.get("name"),
                redemption_code=redemption_code,
                pickup_location="Sala 24 - DC Sala Ruralize",
                office_hours="14h - 18h",
                days_valid=7
            )

            if not email_sent:
                logger.error(f"Failed to send email to {user_email}")
                return {
                    "success": False,
                    "message": "Erro ao enviar e-mail de confirmação. Por favor, tente novamente",
                    "error_code": "EMAIL_SEND_ERROR"
                }

            logger.info(f"Email sent successfully to {user_email}")

            # Step 6 & 7: Deduct points and record redemption
            # Deduct points (amount is negative)
            transaction_data = {
                "user_id": user_id,
                "amount": -points_required,
                "transaction_type": "reward_redemption",
                "description": f"Resgate de recompensa: {reward.get('name')}",
                "related_id": reward_id
            }

            transaction_id = self.points_repo.create_transaction(transaction_data)
            logger.info(f"Points transaction created: {transaction_id}")

            # Record redemption
            redemption_data = {
                "user_id": user_id,
                "user_email": user_email,
                "user_name": user_name,
                "reward_id": reward_id,
                "reward_name": reward.get("name"),
                "points_deducted": points_required,
                "redemption_code": redemption_code,
                "pickup_deadline": pickup_deadline,
                "status": "confirmed",
                "email_sent_at": datetime.utcnow()
            }

            redemption_id = self.reward_repo.create_redemption(redemption_data)
            logger.info(f"Redemption recorded: {redemption_id}")

            # Increment quantity redeemed for the reward
            self.reward_repo.increment_quantity_redeemed(reward_id)

            # Step 8: Return response
            return {
                "success": True,
                "message": "Recompensa resgatada com sucesso! Verifique seu e-mail para os detalhes",
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
                    "status": "confirmed",
                    "email_sent_at": datetime.utcnow().isoformat()
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
