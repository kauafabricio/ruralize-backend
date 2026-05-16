from bson import ObjectId

class UserRepository:

    def __init__(self, db):
        # conecta na coleção "users"
        self.collection = db["users"]

    def find_by_id(self, user_id: str):
        try:
            return self.collection.find_one({"_id": ObjectId(user_id)})
        except Exception:
            return self.collection.find_one({"_id": user_id})

    # busca usuário por email
    def find_by_email(self, email: str):
        return self.collection.find_one({"email": email})

    # busca usuário por matrícula
    def find_by_registration(self, registration: int):
        return self.collection.find_one({"registration": registration})

    # cria usuário
    def create_user(self, user_data: dict):
        return self.collection.insert_one(user_data)