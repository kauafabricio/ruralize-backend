from bson import ObjectId
from datetime import datetime


class EventRepository:

    def __init__(self, db):
        self.collection = db["events"]

    def _serialize(self, event):
        return {
            "id": str(event["_id"]),
            "title": event["title"],
            "description": event["description"],
            "promoter_id": event["promoter_id"],
            "action_id": event["action_id"],
            "start_date": event["start_date"],
            "end_date": event["end_date"],
            "location_name": event["location_name"],
            "address": event["address"],
            "latitude": event.get("latitude"),
            "longitude": event.get("longitude"),
            "max_participants": event["max_participants"],
            "points": event["points"],
            "status": event["status"],
            "photo_url": event.get("photo_url"),
            "created_at": event["created_at"],
            "updated_at": event["updated_at"],
            "participant_count": event.get("participant_count", 0)
        }

    def create_event(self, event_data):
        event_data["created_at"] = datetime.utcnow()
        event_data["updated_at"] = datetime.utcnow()
        event_data["participant_count"] = 0
        event_data["participants"] = []

        result = self.collection.insert_one(event_data)
        return str(result.inserted_id)

    def get_all_events(self):
        events = self.collection.find()
        return [self._serialize(e) for e in events]

    def get_event_by_id(self, event_id):
        try:
            obj_id = ObjectId(event_id)
        except Exception:
            obj_id = event_id

        event = self.collection.find_one({"_id": obj_id})
        return self._serialize(event) if event else None

    def get_events_by_filter(self, filters):
        """Get events with filters: action_id, status, date range"""
        query = {}

        if filters.get("action_id"):
            query["action_id"] = filters["action_id"]

        if filters.get("status"):
            query["status"] = filters["status"]

        if filters.get("start_date") or filters.get("end_date"):
            date_query = {}
            if filters.get("start_date"):
                date_query["$gte"] = filters["start_date"]
            if filters.get("end_date"):
                date_query["$lte"] = filters["end_date"]
            if date_query:
                query["start_date"] = date_query

        events = self.collection.find(query)
        return [self._serialize(e) for e in events]

    def get_events_by_promoter(self, promoter_id):
        events = self.collection.find({"promoter_id": promoter_id})
        return [self._serialize(e) for e in events]

    def update_event(self, event_id, update_data):
        try:
            obj_id = ObjectId(event_id)
        except Exception:
            obj_id = event_id

        update_data["updated_at"] = datetime.utcnow()

        return self.collection.update_one(
            {"_id": obj_id},
            {"$set": update_data}
        )

    def delete_event(self, event_id):
        try:
            obj_id = ObjectId(event_id)
        except Exception:
            obj_id = event_id

        return self.collection.delete_one({"_id": obj_id})

    def increment_participant_count(self, event_id):
        try:
            obj_id = ObjectId(event_id)
        except Exception:
            obj_id = event_id

        return self.collection.update_one(
            {"_id": obj_id},
            {"$inc": {"participant_count": 1}}
        )

    def decrement_participant_count(self, event_id):
        try:
            obj_id = ObjectId(event_id)
        except Exception:
            obj_id = event_id

        return self.collection.update_one(
            {"_id": obj_id},
            {"$inc": {"participant_count": -1}}
        )

    def register_user(self, event_id, user_id):
        try:
            obj_id = ObjectId(event_id)
        except Exception:
            obj_id = event_id

        return self.collection.update_one(
            {
                "_id": obj_id,
                "participants": {"$ne": user_id}
            },
            {
                "$push": {"participants": user_id},
                "$inc": {"participant_count": 1}
            }
        )

    def unregister_user(self, event_id, user_id):
        try:
            obj_id = ObjectId(event_id)
        except Exception:
            obj_id = event_id

        return self.collection.update_one(
            {"_id": obj_id},
            {
                "$pull": {"participants": user_id},
                "$inc": {"participant_count": -1}
            }
        )

    def get_events_by_participant(self, user_id):
        events = self.collection.find({
            "participants": user_id
        })

        return [self._serialize(e) for e in events]
