from bson import ObjectId
from datetime import datetime


class RewardRepository:

    def __init__(self, db):
        self.collection = db["rewards"]
        self.redemptions_collection = db["reward_redemptions"]

    def _serialize(self, reward):
        if not reward:
            return None
        return {
            "id": str(reward["_id"]),
            "name": reward["name"],
            "description": reward["description"],
            "points_required": reward["points_required"],
            "category": reward["category"],
            "image_url": reward.get("image_url"),
            "quantity_available": reward.get("quantity_available"),
            "quantity_redeemed": reward.get("quantity_redeemed", 0),
            "created_at": reward["created_at"]
        }

    def _serialize_redemption(self, redemption):
        if not redemption:
            return None
        return {
            "id": str(redemption["_id"]),
            "user_id": redemption["user_id"],
            "reward_id": redemption["reward_id"],
            "reward_name": redemption["reward_name"],
            "points_deducted": redemption["points_deducted"],
            "redeemed_at": redemption["redeemed_at"]
        }

    def create_reward(self, reward_data):
        """Create a new reward"""
        reward_data["created_at"] = datetime.utcnow()
        reward_data["quantity_redeemed"] = 0

        result = self.collection.insert_one(reward_data)
        return str(result.inserted_id)

    def get_reward_by_id(self, reward_id):
        try:
            obj_id = ObjectId(reward_id)
        except Exception:
            obj_id = reward_id

        reward = self.collection.find_one({"_id": obj_id})
        return self._serialize(reward)

    def get_all_rewards(self):
        """Get all available rewards"""
        rewards = self.collection.find().sort("created_at", -1)
        return [self._serialize(r) for r in rewards]

    def get_rewards_by_category(self, category):
        """Get rewards by category"""
        rewards = self.collection.find({"category": category}).sort("created_at", -1)
        return [self._serialize(r) for r in rewards]

    def update_reward(self, reward_id, update_data):
        """Update reward details"""
        try:
            obj_id = ObjectId(reward_id)
        except Exception:
            obj_id = reward_id

        result = self.collection.update_one(
            {"_id": obj_id},
            {"$set": update_data}
        )
        return result.modified_count > 0

    def increment_quantity_redeemed(self, reward_id):
        """Increment quantity redeemed for a reward"""
        try:
            obj_id = ObjectId(reward_id)
        except Exception:
            obj_id = reward_id

        self.collection.update_one(
            {"_id": obj_id},
            {"$inc": {"quantity_redeemed": 1}}
        )

    def delete_reward(self, reward_id):
        """Delete a reward"""
        try:
            obj_id = ObjectId(reward_id)
        except Exception:
            obj_id = reward_id

        return self.collection.delete_one({"_id": obj_id})

    def create_redemption(self, redemption_data):
        """Record a reward redemption"""
        redemption_data["redeemed_at"] = datetime.utcnow()

        result = self.redemptions_collection.insert_one(redemption_data)
        return str(result.inserted_id)

    def get_redemptions_by_user(self, user_id):
        """Get all redemptions for a user"""
        redemptions = self.redemptions_collection.find(
            {"user_id": user_id}
        ).sort("redeemed_at", -1)
        return [self._serialize_redemption(r) for r in redemptions]

    def get_redemptions_by_reward(self, reward_id):
        """Get all redemptions for a reward"""
        redemptions = self.redemptions_collection.find(
            {"reward_id": reward_id}
        ).sort("redeemed_at", -1)
        return [self._serialize_redemption(r) for r in redemptions]

    def count_redemptions_for_user_reward(self, user_id, reward_id):
        """Count how many times user redeemed a specific reward"""
        return self.redemptions_collection.count_documents({
            "user_id": user_id,
            "reward_id": reward_id
        })
