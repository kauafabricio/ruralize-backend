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

    def find_by_role(self, role: str):
        users = self.users_collection.find({"role": role})
        return [self._serialize(u) for u in users]

    def find_by_tags(self, tags: list):
        users = self.users_collection.find({
            "tags": {"$in": tags}
        })
        return [self._serialize(u) for u in users]
