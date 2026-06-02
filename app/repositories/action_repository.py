from bson import ObjectId
from datetime import datetime


class ActionRepository:

    def __init__(self, db):
        self.collection = db["actions"]

    def _serialize(self, action):
        return {
            "id": str(action["_id"]),
            "name": action["name"],
            "description": action["description"]
        }

    def create_action(self, action_data):
        result = self.collection.insert_one(action_data)
        return str(result.inserted_id)

    def get_all_actions(self):
        actions = self.collection.find()
        return [self._serialize(a) for a in actions]

    def get_action_by_id(self, action_id):
        try:
            obj_id = ObjectId(action_id)
        except Exception:
            obj_id = action_id

        action = self.collection.find_one({"_id": obj_id})
        return self._serialize(action) if action else None

    def update_action(self, action_id, update_data):
        try:
            obj_id = ObjectId(action_id)
        except Exception:
            obj_id = action_id

        return self.collection.update_one(
            {"_id": obj_id},
            {"$set": update_data}
        )

    def delete_action(self, action_id):
        try:
            obj_id = ObjectId(action_id)
        except Exception:
            obj_id = action_id

        return self.collection.delete_one({"_id": obj_id})
