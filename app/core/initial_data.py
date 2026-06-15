from app.repositories.reward_repository import RewardRepository
from app.database import db


def ensure_default_rewards():
    """Create or update default reward entries on application startup."""
    reward_repo = RewardRepository(db)

    default_rewards = [
        {
            "name": "10 fichas de almoço no RU",
            "description": "Troque seus pontos por 10 fichas de almoço no Restaurante Universitário.",
            "points_required": 150,
            "category": "food",
            "image_url": None,
            "quantity_available": None,
        },
        {
            "name": "10 fichas de jantar no RU",
            "description": "Troque seus pontos por 10 fichas de jantar no Restaurante Universitário.",
            "points_required": 150,
            "category": "food",
            "image_url": None,
            "quantity_available": None,
        },
        {
            "name": "1 ecobag",
            "description": "Resgate uma ecobag ecológica para suas compras e reduza o uso de plástico.",
            "points_required": 300,
            "category": "other",
            "image_url": None,
            "quantity_available": 50,
        },
    ]

    for reward_data in default_rewards:
        reward_repo.upsert_reward_by_name(reward_data)
