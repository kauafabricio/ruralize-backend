from datetime import datetime


class SustainableActionRepository:

    def __init__(self, db):
        self.collection = db["sustainable_actions"]

    def _serialize(self, action):
        return {
            "id": action.get("id"),
            "name": action["name"],
            "icon": action.get("icon", "🌱"),
            "is_default": action.get("is_default", False),
            "created_by": action.get("created_by"),
            "created_at": action["created_at"]
        }

    def create_action(self, action_data):
        action_data["created_at"] = datetime.utcnow()
        result = self.collection.insert_one(action_data)
        return str(result.inserted_id)

    def get_all_actions(self):
        actions = self.collection.find().sort("is_default", -1)
        return [self._serialize(a) for a in actions]

    def get_action_by_id(self, action_id: str):
        action = self.collection.find_one({"id": action_id})
        return self._serialize(action) if action else None

    def get_action_by_name(self, name: str):
        action = self.collection.find_one({"name": name})
        return self._serialize(action) if action else None

    def action_exists(self, action_id: str):
        return self.collection.find_one({"id": action_id}) is not None

    def update_action(self, action_id: str, update_data):
        return self.collection.update_one(
            {"id": action_id},
            {"$set": update_data}
        )

    def delete_action(self, action_id: str):
        return self.collection.delete_one({"id": action_id})

    def delete_all_actions(self):
        return self.collection.delete_many({})
