from bson import ObjectId
from datetime import datetime


class PointsRepository:

    def __init__(self, db):
        self.collection = db["points_transactions"]
        self.users_collection = db["users"]

    def _serialize(self, transaction):
        return {
            "id": str(transaction["_id"]),
            "user_id": transaction["user_id"],
            "amount": transaction["amount"],
            "transaction_type": transaction["transaction_type"],
            "description": transaction["description"],
            "related_id": transaction.get("related_id"),
            "created_at": transaction["created_at"]
        }

    def create_transaction(self, transaction_data, session=None):
        """Create a points transaction and update user balance"""
        transaction_data["created_at"] = datetime.utcnow()

        if session is not None:
            result = self.collection.insert_one(transaction_data, session=session)
            self.users_collection.update_one(
                {"_id": ObjectId(transaction_data["user_id"])},
                {"$inc": {"points_balance": transaction_data["amount"]}},
                session=session
            )
        else:
            result = self.collection.insert_one(transaction_data)
            self.users_collection.update_one(
                {"_id": ObjectId(transaction_data["user_id"])},
                {"$inc": {"points_balance": transaction_data["amount"]}}
            )

        return str(result.inserted_id)

    def get_transaction_by_id(self, transaction_id):
        try:
            obj_id = ObjectId(transaction_id)
        except Exception:
            obj_id = transaction_id

        transaction = self.collection.find_one({"_id": obj_id})
        return self._serialize(transaction) if transaction else None

    def get_transactions_by_user(self, user_id):
        """Get all points transactions for a user"""
        transactions = self.collection.find(
            {"user_id": user_id}
        ).sort("created_at", -1)
        return [self._serialize(t) for t in transactions]

    def get_user_balance(self, user_id):
        """Get current points balance for a user"""
        user = self.users_collection.find_one({"_id": ObjectId(user_id)})
        if not user:
            return None

        balance = user.get("points_balance", 0)

        # Calculate totals from transactions
        earned = self.collection.aggregate([
            {"$match": {"user_id": user_id, "amount": {"$gt": 0}}},
            {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
        ])
        earned_total = list(earned)[0]["total"] if list(self.collection.aggregate([
            {"$match": {"user_id": user_id, "amount": {"$gt": 0}}},
            {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
        ])) else 0

        spent = self.collection.aggregate([
            {"$match": {"user_id": user_id, "amount": {"$lt": 0}}},
            {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
        ])
        spent_total = abs(list(spent)[0]["total"]) if list(self.collection.aggregate([
            {"$match": {"user_id": user_id, "amount": {"$lt": 0}}},
            {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
        ])) else 0

        return {
            "user_id": user_id,
            "balance": balance,
            "total_earned": earned_total,
            "total_spent": spent_total
        }

    def count_transactions(self, user_id):
        """Count transactions for a user"""
        return self.collection.count_documents({"user_id": user_id})
