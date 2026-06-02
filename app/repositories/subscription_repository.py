from bson import ObjectId
from datetime import datetime


class SubscriptionRepository:

    def __init__(self, db):
        self.collection = db["event_subscriptions"]

    def _serialize(self, subscription):
        return {
            "id": str(subscription["_id"]),
            "user_id": subscription["user_id"],
            "event_id": subscription["event_id"],
            "status": subscription["status"],
            "created_at": subscription["created_at"]
        }

    def create_subscription(self, subscription_data):
        subscription_data["created_at"] = datetime.utcnow()

        result = self.collection.insert_one(subscription_data)
        return str(result.inserted_id)

    def get_subscription_by_id(self, subscription_id):
        try:
            obj_id = ObjectId(subscription_id)
        except Exception:
            obj_id = subscription_id

        subscription = self.collection.find_one({"_id": obj_id})
        return self._serialize(subscription) if subscription else None

    def get_subscription(self, user_id, event_id):
        """Check if user is already subscribed to event"""
        subscription = self.collection.find_one({
            "user_id": user_id,
            "event_id": event_id
        })
        return self._serialize(subscription) if subscription else None

    def get_subscriptions_by_user(self, user_id):
        subscriptions = self.collection.find({"user_id": user_id})
        return [self._serialize(s) for s in subscriptions]

    def get_subscriptions_by_event(self, event_id):
        subscriptions = self.collection.find({"event_id": event_id})
        return [self._serialize(s) for s in subscriptions]

    def get_participants_by_event(self, event_id, status="subscribed"):
        """Get participants for event with specific status"""
        subscriptions = self.collection.find({
            "event_id": event_id,
            "status": status
        })
        return [self._serialize(s) for s in subscriptions]

    def count_subscribed(self, event_id):
        """Count how many users are subscribed (not attended/missed)"""
        return self.collection.count_documents({
            "event_id": event_id,
            "status": "subscribed"
        })

    def update_subscription(self, subscription_id, update_data):
        try:
            obj_id = ObjectId(subscription_id)
        except Exception:
            obj_id = subscription_id

        return self.collection.update_one(
            {"_id": obj_id},
            {"$set": update_data}
        )

    def delete_subscription(self, subscription_id):
        try:
            obj_id = ObjectId(subscription_id)
        except Exception:
            obj_id = subscription_id

        return self.collection.delete_one({"_id": obj_id})

    def delete_subscription_by_user_event(self, user_id, event_id):
        """Delete subscription by user and event IDs"""
        return self.collection.delete_one({
            "user_id": user_id,
            "event_id": event_id
        })
