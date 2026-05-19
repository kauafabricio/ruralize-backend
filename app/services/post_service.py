from fastapi import HTTPException
from app.repositories.post_repository import PostRepository
from app.schemas.post_schema import PostCreate, PostUpdate, CommentCreate


class PostService:

    def __init__(self, post_repo: PostRepository, profile_repo=None):
        self.post_repo = post_repo
        self.profile_repo = profile_repo

    def _enrich_post(self, post):
        """Enriquece o post com dados de perfil dos comentaristas e curtiadores."""
        if not self.profile_repo:
            return post

        enriched_post = post.copy()

        # Enriquecer comentários com nome e foto
        enriched_comments = []
        for comment in post.get("comments", []):
            profile = self.profile_repo.find_by_user_id(comment["user_id"])
            enriched_comments.append({
                "user_id": comment["user_id"],
                "user_name": profile.get("name", "Usuário Desconhecido") if profile else "Usuário Desconhecido",
                "user_photo": profile.get("profile_photo_url") if profile else None,
                "content": comment["content"],
                "created_at": comment["created_at"]
            })
        enriched_post["comments"] = enriched_comments

        # Enriquecer curtidas com nome e foto
        enriched_liked_by = []
        for user_id in post.get("liked_by", []):
            profile = self.profile_repo.find_by_user_id(user_id)
            enriched_liked_by.append({
                "user_id": user_id,
                "user_name": profile.get("name", "Usuário Desconhecido") if profile else "Usuário Desconhecido",
                "user_photo": profile.get("profile_photo_url") if profile else None
            })
        enriched_post["liked_by"] = enriched_liked_by

        return enriched_post

    def get_all_posts(self):
        # retorna todas as postagens do banco sem filtro adicional
        posts = self.post_repo.get_all_posts()
        return [self._enrich_post(p) for p in posts]

    def get_post(self, post_id: str):
        # retorna uma postagem específica por id
        post = self.post_repo.get_post_by_id(post_id)
        if not post:
            raise HTTPException(status_code=404, detail="Post não encontrado")
        return self._enrich_post(post)

    def create_post(self, post_data: PostCreate, user_id: str):
        # cria uma nova postagem incluindo o user_id do autor
        payload = post_data.dict()
        payload["user_id"] = user_id
        post_id = self.post_repo.create_post(payload)
        return {"message": "Post criado com sucesso", "id": post_id}

    def update_post(self, post_id: str, post_data: PostUpdate):
        # atualiza somente os campos recebidos no payload
        update_payload = {k: v for k, v in post_data.dict().items() if v is not None}
        if not update_payload:
            raise HTTPException(status_code=400, detail="Nenhum campo para atualizar")

        result = self.post_repo.update_post(post_id, update_payload)
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Post não encontrado")

        return {"message": "Post atualizado com sucesso"}

    def like_post(self, post_id: str, user_id: str = None):
        # registra um like e guarda o user_id no array liked_by se fornecido
        result = self.post_repo.like_post(post_id, user_id)
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Post não encontrado")
        if result.modified_count == 0 and user_id:
            # se o usuário já curtiu antes, não altera a contagem
            return {"message": "Like já registrado"}
        return {"message": "Like registrado com sucesso"}

    def add_comment(self, post_id: str, comment_data: CommentCreate):
        # adiciona comentário com user_id e texto no post
        result = self.post_repo.add_comment(post_id, comment_data.user_id, comment_data.content)
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Post não encontrado")
        return {"message": "Comentário adicionado com sucesso"}

    def delete_post(self, post_id: str, user_id: str):
        # valida se o usuário é o dono do post antes de deletar
        post = self.post_repo.get_post_by_id(post_id)
        if not post:
            raise HTTPException(status_code=404, detail="Post não encontrado")

        if post["user_id"] != user_id:
            raise HTTPException(status_code=403, detail="Você não tem permissão para deletar este post")

        result = self.post_repo.delete_post(post_id)
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Post não encontrado")

        return {"message": "Post deletado com sucesso"}

    def remove_like(self, post_id: str, user_id: str):
        # remove a curtida (like) de um post
        result = self.post_repo.remove_like(post_id, user_id)
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Post não encontrado ou like não registrado")
        if result.modified_count == 0:
            return {"message": "Like não estava registrado"}
        return {"message": "Like removido com sucesso"}

    def remove_comment(self, post_id: str, comment_index: int, user_id: str):
        # valida se o usuário é o dono do comentário antes de deletar
        post = self.post_repo.get_post_by_id(post_id)
        if not post:
            raise HTTPException(status_code=404, detail="Post não encontrado")

        if not (0 <= comment_index < len(post.get("comments", []))):
            raise HTTPException(status_code=404, detail="Comentário não encontrado")

        comment = post["comments"][comment_index]
        if comment["user_id"] != user_id:
            raise HTTPException(status_code=403, detail="Você não tem permissão para deletar este comentário")

        result = self.post_repo.remove_comment(post_id, comment_index)
        if not result:
            raise HTTPException(status_code=400, detail="Erro ao deletar comentário")

        return {"message": "Comentário deletado com sucesso"}
