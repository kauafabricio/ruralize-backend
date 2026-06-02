from fastapi import HTTPException
from app.repositories.subscription_repository import SubscriptionRepository
from app.repositories.event_repository import EventRepository
from app.schemas.subscription_schema import SubscriptionCreate, SubscriptionUpdate


class SubscriptionService:

    def __init__(self, subscription_repo: SubscriptionRepository, event_repo: EventRepository = None):
        self.subscription_repo = subscription_repo
        self.event_repo = event_repo

    def get_subscription(self, subscription_id: str):
        subscription = self.subscription_repo.get_subscription_by_id(subscription_id)
        if not subscription:
            raise HTTPException(status_code=404, detail="Inscrição não encontrada")
        return subscription

    def get_subscriptions_by_user(self, user_id: str):
        return self.subscription_repo.get_subscriptions_by_user(user_id)

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

    def update_subscription_status(self, event_id: str, current_user: dict, status_data: SubscriptionUpdate):
        """Update subscription status (attended/missed) - only event promoter can do this"""
        user_id = current_user["id"]

        # Check if user is event promoter
        if self.event_repo:
            event = self.event_repo.get_event_by_id(event_id)
            if not event:
                raise HTTPException(status_code=404, detail="Evento não encontrado")

            if event["promoter_id"] != user_id:
                raise HTTPException(status_code=403, detail="Você não tem permissão para atualizar inscrições neste evento")

        # Validate status
        valid_statuses = ["subscribed", "attended", "missed"]
        if status_data.status not in valid_statuses:
            raise HTTPException(status_code=400, detail=f"Status deve ser um de: {', '.join(valid_statuses)}")

        # This endpoint would need a way to know which user to update - typically needs user_id in request
        # For now, this is a template; actual implementation would need user_id parameter
        raise HTTPException(status_code=400, detail="Implementação incompleta - forneça user_id no request")
