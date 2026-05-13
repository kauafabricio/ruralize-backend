from bson import ObjectId
from datetime import datetime

class PostRepository:

    def __init__(self, db):
        self.collection = db["posts"]

    def _serialize(self, post):
        return {
            "id": str(post["_id"]),
            "user_id": post["user_id"],
            "content": post["content"],
            "location": post.get("location"),
            "sustainable_action": post.get("sustainable_action"),
            "event_id": post.get("event_id"),
            "image_url": post.get("image_url"),
            "likes": post.get("likes", 0),
            "comments": post.get("comments", []),
            "created_at": post["created_at"]
        }

    def create_post(self, post_data):
        post_data["created_at"] = datetime.utcnow()
        post_data["likes"] = 0
        post_data["comments"] = []

        result = self.collection.insert_one(post_data)
        return str(result.inserted_id)

    def get_all_posts(self):
        posts = self.collection.find()
        return [self._serialize(p) for p in posts]

    def get_posts_by_users(self, user_ids):
        posts = self.collection.find({
            "user_id": {"$in": user_ids}
        })
        return [self._serialize(p) for p in posts]

    def like_post(self, post_id):
        self.collection.update_one(
            {"_id": ObjectId(post_id)},
            {"$inc": {"likes": 1}}
        )

    def add_comment(self, post_id, comment):
        self.collection.update_one(
            {"_id": ObjectId(post_id)},
            {"$push": {"comments": comment}}
        )