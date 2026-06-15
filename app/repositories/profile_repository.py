from bson import ObjectId


class ProfileRepository:

    def __init__(self, db):
        self.users_collection = db["users"]

    def _serialize(self, user):
        return {
            "id": str(user["_id"]),
            "name": user["name"],
            "role": user["role"],
            "course": user.get("course"),
            "department": user.get("department"),
            "description": user.get("description"),
            "profile_photo_url": user.get("profile_photo_url"),
            "cover_photo_url": user.get("cover_photo_url"),
            "tags": user.get("tags", []),
            "academic_info": {
                "email": user.get("email"),
                "registration": user.get("registration"),
                "campus_location": user.get("campus_location")
            }
        }

    def find_by_user_id(self, user_id: str):
        try:
            obj_id = ObjectId(user_id)
        except Exception:
            obj_id = user_id

        user = self.users_collection.find_one({"_id": obj_id})
        return self._serialize(user) if user else None

    def update_by_user_id(self, user_id: str, update_data: dict):
        try:
            obj_id = ObjectId(user_id)
        except Exception:
            obj_id = user_id

        return self.users_collection.update_one(
            {"_id": obj_id},
            {"$set": update_data}
        )

    def get_all_profiles(self):
        users = self.users_collection.find()
        return [self._serialize(u) for u in users]

    def find_by_name(self, name: str):
        users = self.users_collection.find({
            "name": {"$regex": name, "$options": "i"}
        })
        return [self._serialize(u) for u in users]

    def find_by_course(self, course: str):
        users = self.users_collection.find({"course": course})
        return [self._serialize(u) for u in users]

    def find_by_department(self, department: str):
        users = self.users_collection.find({"department": department})
        return [self._serialize(u) for u in users]

    def find_by_user_ids(self, user_ids: list):
        object_ids = []
        for user_id in user_ids:
            try:
                object_ids.append(ObjectId(user_id))
            except Exception:
                object_ids.append(user_id)

        users = self.users_collection.find({"_id": {"$in": object_ids}})
        return [self._serialize(u) for u in users]

    def find_raw_by_user_id(self, user_id: str):
        try:
            obj_id = ObjectId(user_id)
        except Exception:
            obj_id = user_id

        return self.users_collection.find_one({"_id": obj_id})

    def add_follow(self, user_id: str, target_id: str):
        try:
            obj_id = ObjectId(user_id)
        except Exception:
            obj_id = user_id

        return self.users_collection.update_one(
            {"_id": obj_id},
            {"$addToSet": {"following": target_id}}
        )

    def remove_follow(self, user_id: str, target_id: str):
        try:
            obj_id = ObjectId(user_id)
        except Exception:
            obj_id = user_id

        return self.users_collection.update_one(
            {"_id": obj_id},
            {"$pull": {"following": target_id}}
        )

    def add_follower(self, user_id: str, follower_id: str):
        try:
            obj_id = ObjectId(user_id)
        except Exception:
            obj_id = user_id

        return self.users_collection.update_one(
            {"_id": obj_id},
            {"$addToSet": {"followers": follower_id}}
        )

    def remove_follower(self, user_id: str, follower_id: str):
        try:
            obj_id = ObjectId(user_id)
        except Exception:
            obj_id = user_id

        return self.users_collection.update_one(
            {"_id": obj_id},
            {"$pull": {"followers": follower_id}}
        )

    def get_following_ids(self, user_id: str):
        user = self.find_raw_by_user_id(user_id)
        if not user:
            return None
        return user.get("following", [])

    def get_followers_ids(self, user_id: str):
        user = self.find_raw_by_user_id(user_id)
        if not user:
            return None
        return user.get("followers", [])

    def is_following(self, user_id: str, target_id: str):
        try:
            obj_id = ObjectId(user_id)
        except Exception:
            obj_id = user_id

        user = self.users_collection.find_one({"_id": obj_id, "following": target_id})
        return user is not None

    def find_by_role(self, role: str):
        users = self.users_collection.find({"role": role})
        return [self._serialize(u) for u in users]

    def find_by_tags(self, tags: list):
        users = self.users_collection.find({
            "tags": {"$in": tags}
        })
        return [self._serialize(u) for u in users]
