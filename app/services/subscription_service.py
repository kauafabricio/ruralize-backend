from fastapi import HTTPException
from app.repositories.subscription_repository import SubscriptionRepository
from app.repositories.event_repository import EventRepository
from app.repositories.points_repository import PointsRepository
from app.schemas.subscription_schema import SubscriptionCreate, SubscriptionUpdate


class SubscriptionService:

    def __init__(
        self,
        subscription_repo: SubscriptionRepository,
        event_repo: EventRepository = None,
        points_repo: PointsRepository = None,
    ):
        self.subscription_repo = subscription_repo
        self.event_repo = event_repo
        self.points_repo = points_repo

    def get_subscription(self, subscription_id: str):
        subscription = self.subscription_repo.get_subscription_by_id(subscription_id)
        if not subscription:
            raise HTTPException(status_code=404, detail="Inscrição não encontrada")
        return subscription

    def get_subscription_for_user_event(self, event_id: str, current_user: dict):
        return self.subscription_repo.get_subscription(current_user["id"], event_id)

    # def get_subscriptions_by_user(self, user_id: str):
    #     return self.subscription_repo.get_subscriptions_by_user(user_id)

    def get_participants(self, event_id: str):
        """Get all participants of an event"""
        participants = self.subscription_repo.get_subscriptions_by_event(event_id)
        return [{"user_id": p["user_id"], "status": p["status"]} for p in participants]

    def subscribe(self, event_id: str, current_user: dict):
        """Subscribe user to event"""
        user_id = current_user["id"]

        # Check if event exists
        if self.event_repo:
            event = self.event_repo.get_event_by_id(event_id)
            if not event:
                raise HTTPException(status_code=404, detail="Evento não encontrado")

            # Check if event is at capacity
            current_count = self.subscription_repo.count_subscribed(event_id)
            if current_count >= event["max_participants"]:
                raise HTTPException(status_code=400, detail="Evento cheio")

        # Check if already subscribed
        existing = self.subscription_repo.get_subscription(user_id, event_id)
        if existing:
            raise HTTPException(status_code=400, detail="Você já está inscrito neste evento")

        # Create subscription
        subscription_data = {
            "user_id": user_id,
            "event_id": event_id,
            "status": "subscribed"
        }

        subscription_id = self.subscription_repo.create_subscription(subscription_data)

        # Increment event participant count
        if self.event_repo:
            self.event_repo.increment_participant_count(event_id)

        return {"message": "Inscrição realizada com sucesso", "id": subscription_id}

    def unsubscribe(self, event_id: str, current_user: dict):
        """Unsubscribe user from event"""
        user_id = current_user["id"]

        # Check if subscription exists
        existing = self.subscription_repo.get_subscription(user_id, event_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Inscrição não encontrada")

        # Delete subscription
        result = self.subscription_repo.delete_subscription_by_user_event(user_id, event_id)
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Inscrição não encontrada")

        # Decrement event participant count
        if self.event_repo:
            self.event_repo.decrement_participant_count(event_id)

        return {"message": "Inscrição cancelada com sucesso"}

    def update_subscription_status(
        self,
        event_id: str,
        current_user: dict,
        participant_user_id: str,
        status_data: SubscriptionUpdate,
    ):
        """Update subscription status (attended/missed) - only event promoter can do this"""
        promoter_id = current_user["id"]

        # Check if user is event promoter
        if self.event_repo:
            event = self.event_repo.get_event_by_id(event_id)
            if not event:
                raise HTTPException(status_code=404, detail="Evento não encontrado")

            if event["promoter_id"] != promoter_id:
                raise HTTPException(status_code=403, detail="Você não tem permissão para atualizar inscrições neste evento")

        # Validate status
        valid_statuses = ["subscribed", "attended", "missed"]
        if status_data.status not in valid_statuses:
            raise HTTPException(status_code=400, detail=f"Status deve ser um de: {', '.join(valid_statuses)}")

        # Check if subscription exists
        existing = self.subscription_repo.get_subscription(participant_user_id, event_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Inscrição não encontrada")

        # If the status is already set, return a neutral response
        if existing["status"] == status_data.status:
            return {
                "message": "Status da inscrição já está atualizado",
                "status": existing["status"],
            }

        result = self.subscription_repo.update_subscription_by_user_event(
            participant_user_id,
            event_id,
            {"status": status_data.status},
        )

        if result.modified_count == 0:
            raise HTTPException(status_code=400, detail="Falha ao atualizar o status da inscrição")

        if status_data.status == "attended" and self.points_repo and self.event_repo:
            event = self.event_repo.get_event_by_id(event_id)
            if event and event.get("points", 0) > 0:
                self.points_repo.create_transaction({
                    "user_id": participant_user_id,
                    "amount": event["points"],
                    "transaction_type": "credit",
                    "description": f"Pontos de presença no evento {event['title']}",
                    "related_id": event_id,
                })

        return {
            "message": "Status da presença atualizado com sucesso",
            "status": status_data.status,
        }
    
    def get_subscriptions_by_user(self, user_id: str):
        subscriptions = self.subscription_repo.get_subscriptions_by_user(user_id)
        result = []
        for sub in subscriptions:
        # Busca os detalhes do evento usando o event_id da inscrição
            event_data = self.event_repo.get_event_by_id(sub["event_id"])
        
            if event_data:
                # Monta a estrutura combinada
                result.append({
                    "id": sub["id"],
                    "status": sub["status"],
                    "created_at": sub["created_at"],
                    "event": {
                        "id": str(event_data["_id"]) if "_id" in event_data else event_data.get("id"),
                        "title": event_data.get("title"),
                        "description": event_data.get("description"),
                        "start_date": event_data.get("start_date"),
                        "location_name": event_data.get("location_name")
                    }
                })
        return result
