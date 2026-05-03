class UserRepository:

    def __init__(self, db):
        # conecta na coleção "users"
        self.collection = db["users"]

    # busca usuário por email
    def find_by_email(self, email: str):
        return self.collection.find_one({"email": email})

    # busca usuário por matrícula
    def find_by_registration(self, registration: int):
        return self.collection.find_one({"registration": registration})

    # cria usuário
    def create_user(self, user_data: dict):
        return self.collection.insert_one(user_data)