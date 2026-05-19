from bson import ObjectId
from datetime import datetime


class ProfileRepository:

    def __init__(self, db):
        self.collection = db["profiles"]

    def _serialize(self, profile):
        return {
            "id": str(profile["_id"]),
            "user_id": profile["user_id"],
            "name": profile["name"],
            "role": profile["role"],
            "course": profile.get("course"),
            "department": profile.get("department"),
            "description": profile.get("description"),
            "profile_photo_url": profile.get("profile_photo_url"),
            "cover_photo_url": profile.get("cover_photo_url"),
            "tags": profile.get("tags", []),
            "academic_info": {
                "email": profile.get("email"),
                "registration": profile.get("registration"),
                "campus_location": profile.get("campus_location")
            },
            "created_at": profile["created_at"],
            "updated_at": profile["updated_at"]
        }

    def create_profile(self, profile_data: dict):
        profile_data["created_at"] = datetime.utcnow()
        profile_data["updated_at"] = datetime.utcnow()
        result = self.collection.insert_one(profile_data)
        return str(result.inserted_id)

    def find_by_user_id(self, user_id: str):
        try:
            obj_id = ObjectId(user_id)
        except Exception:
            obj_id = user_id

        profile = self.collection.find_one({"user_id": obj_id})
        return self._serialize(profile) if profile else None

    def find_by_id(self, profile_id: str):
        try:
            obj_id = ObjectId(profile_id)
        except Exception:
            obj_id = profile_id

        profile = self.collection.find_one({"_id": obj_id})
        return self._serialize(profile) if profile else None

    def update_profile(self, profile_id: str, update_data: dict):
        try:
            obj_id = ObjectId(profile_id)
        except Exception:
            obj_id = profile_id

        update_data["updated_at"] = datetime.utcnow()

        return self.collection.update_one(
            {"_id": obj_id},
            {"$set": update_data}
        )

    def update_by_user_id(self, user_id: str, update_data: dict):
        try:
            obj_id = ObjectId(user_id)
        except Exception:
            obj_id = user_id

        update_data["updated_at"] = datetime.utcnow()

        return self.collection.update_one(
            {"user_id": obj_id},
            {"$set": update_data}
        )

    def delete_profile(self, profile_id: str):
        try:
            obj_id = ObjectId(profile_id)
        except Exception:
            obj_id = profile_id

        return self.collection.delete_one({"_id": obj_id})

    def get_all_profiles(self):
        profiles = self.collection.find()
        return [self._serialize(p) for p in profiles]

    def find_by_name(self, name: str):
        profiles = self.collection.find({
            "name": {"$regex": name, "$options": "i"}
        })
        return [self._serialize(p) for p in profiles]

    def find_by_course(self, course: str):
        profiles = self.collection.find({"course": course})
        return [self._serialize(p) for p in profiles]

    def find_by_department(self, department: str):
        profiles = self.collection.find({"department": department})
        return [self._serialize(p) for p in profiles]

    def find_by_role(self, role: str):
        profiles = self.collection.find({"role": role})
        return [self._serialize(p) for p in profiles]

    def find_by_tags(self, tags: list):
        profiles = self.collection.find({
            "tags": {"$in": tags}
        })
        return [self._serialize(p) for p in profiles]
