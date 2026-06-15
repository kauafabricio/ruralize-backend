from bson import ObjectId
from datetime import datetime

# Repositório de posts: responsável por criar, consultar e atualizar posts
# Comentários e likes agora armazenam também o `user_id` para permitir
# recuperar informações do autor do like/comentário posteriormente.

class PostRepository:

    def __init__(self, db):
        self.collection = db["posts"]

    def _serialize(self, post):
        return {
            "id": str(post["_id"]),
            "user_id": post["user_id"],
            "content": post["content"],
            "location": post.get("location"),
            "sustainable_action_id": post.get("sustainable_action_id"),
            "sustainable_action": post.get("sustainable_action"),
            "event_id": post.get("event_id"),
            "image_url": post.get("image_url"),
            "likes": post.get("likes", 0),
            "liked_by": post.get("liked_by", []),
            "comments": post.get("comments", []),
            "created_at": post["created_at"]
        }

    def create_post(self, post_data):
        post_data["created_at"] = datetime.utcnow()
        post_data["likes"] = 0
        post_data["comments"] = []
        post_data["liked_by"] = []

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

    def get_posts_by_user_id(self, user_id):
        posts = self.collection.find({
            "user_id": user_id
        }).sort("created_at", -1)
        return [self._serialize(p) for p in posts]

    def get_post_by_id(self, post_id):
        try:
            obj_id = ObjectId(post_id)
        except Exception:
            obj_id = post_id

        post = self.collection.find_one({"_id": obj_id})
        return self._serialize(post) if post else None

    def update_post(self, post_id, update_data):
        try:
            obj_id = ObjectId(post_id)
        except Exception:
            obj_id = post_id

        return self.collection.update_one(
            {"_id": obj_id},
            {"$set": update_data}
        )

    def like_post(self, post_id, user_id: str = None):
        """
        Registra um like no post.

        - Se `user_id` for fornecido, adiciona o `user_id` em `liked_by` (se ainda não estiver)
          e atualiza a contagem `likes` de forma consistente.
        - Se `user_id` não for fornecido, mantém o comportamento antigo (apenas incrementa a contagem).
        """
        try:
            obj_id = ObjectId(post_id)
        except Exception:
            obj_id = post_id

        if user_id:
            # Adiciona o user_id em liked_by apenas se ainda não estiver presente
            return self.collection.update_one(
                {"_id": obj_id, "liked_by": {"$ne": user_id}},
                {"$inc": {"likes": 1}, "$push": {"liked_by": user_id}}
            )
        # comportamento compatível: apenas incrementa a contagem
        return self.collection.update_one(
            {"_id": obj_id},
            {"$inc": {"likes": 1}}
        )

    def add_comment(self, post_id, user_id: str, comment_text: str):
        """
        Adiciona um comentário no post e salva o `user_id` junto do texto e timestamp.

        O comentário salvo tem o formato:
          {"user_id": "...", "text": "...", "created_at": datetime}
        """
        try:
            obj_id = ObjectId(post_id)
        except Exception:
            obj_id = post_id

        comment_obj = {
            "user_id": user_id,
            "content": comment_text,
            "created_at": datetime.utcnow()
        }

        result = self.collection.update_one(
            {"_id": obj_id},
            {"$push": {"comments": comment_obj}}
        )
        return result

    def delete_post(self, post_id: str):
        """Deleta um post pelo ID."""
        try:
            obj_id = ObjectId(post_id)
        except Exception:
            obj_id = post_id

        return self.collection.delete_one({"_id": obj_id})

    def remove_like(self, post_id: str, user_id: str):
        """Remove uma curtida (like) de um post."""
        try:
            obj_id = ObjectId(post_id)
        except Exception:
            obj_id = post_id

        return self.collection.update_one(
            {"_id": obj_id, "liked_by": user_id},
            {"$inc": {"likes": -1}, "$pull": {"liked_by": user_id}}
        )

    def remove_comment(self, post_id: str, comment_index: int):
        """Remove um comentário específico pelo índice."""
        try:
            obj_id = ObjectId(post_id)
        except Exception:
            obj_id = post_id

        post = self.collection.find_one({"_id": obj_id})
        if post and 0 <= comment_index < len(post.get("comments", [])):
            comments = post["comments"]
            comments.pop(comment_index)
            return self.collection.update_one(
                {"_id": obj_id},
                {"$set": {"comments": comments}}
            )
        return None

    def migrate_posts_to_action_ids(self, action_mapping):
        """
        Migra posts antigos que têm sustainable_action como string
        para usar sustainable_action_id como referência.

        action_mapping: dict com { "string_value": "action_id" }
        """
        posts = self.collection.find()
        migrated_count = 0

        for post in posts:
            if "sustainable_action_id" not in post or not post["sustainable_action_id"]:
                action_str = post.get("sustainable_action")
                if action_str:
                    action_id = action_mapping.get(action_str, "tree-planting")
                    self.collection.update_one(
                        {"_id": post["_id"]},
                        {"$set": {"sustainable_action_id": action_id}}
                    )
                    migrated_count += 1

        return migrated_count