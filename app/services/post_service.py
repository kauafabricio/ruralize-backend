from fastapi import HTTPException
from app.repositories.post_repository import PostRepository
from app.schemas.post_schema import PostCreate, PostUpdate, CommentCreate

class PostService:

    def __init__(self, post_repo: PostRepository):
        self.post_repo = post_repo

    def get_all_posts(self):
        # retorna todas as postagens do banco sem filtro adicional
        return self.post_repo.get_all_posts()

    def get_post(self, post_id: str):
        # retorna uma postagem específica por id
        post = self.post_repo.get_post_by_id(post_id)
        if not post:
            raise HTTPException(status_code=404, detail="Post não encontrado")
        return post

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
