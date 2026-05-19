from typing import List
from fastapi import APIRouter, HTTPException
from app.schemas.post_schema import PostCreate, PostUpdate, PostResponse, CommentCreate
from app.services.post_service import PostService
from app.repositories.post_repository import PostRepository
from app.repositories.profile_repository import ProfileRepository
from app.database import db

router = APIRouter()

# instância do repositório e serviço de post
post_repo = PostRepository(db)
profile_repo = ProfileRepository(db)
post_service = PostService(post_repo, profile_repo)

@router.get("/", response_model=List[PostResponse])
def get_posts():
    """Retorna todas as postagens."""
    return post_service.get_all_posts()

@router.get("/{post_id}", response_model=PostResponse)
def get_post(post_id: str):
    """Retorna uma única postagem por id."""
    return post_service.get_post(post_id)

@router.post("/", response_model=dict)
def create_post(post: PostCreate, user_id: str):
    """Cria uma nova postagem para um usuário específico."""
    return post_service.create_post(post, user_id)

@router.put("/{post_id}", response_model=dict)
def update_post(post_id: str, post: PostUpdate):
    """Atualiza campos de uma postagem existente."""
    return post_service.update_post(post_id, post)

@router.post("/{post_id}/like", response_model=dict)
def like_post(post_id: str, user_id: str):
    """Registra um like e salva o id do usuário que curtiu."""
    return post_service.like_post(post_id, user_id)

@router.post("/{post_id}/comment", response_model=dict)
def add_comment(post_id: str, comment: CommentCreate):
    """Adiciona um comentário à postagem com user_id e conteúdo."""
    return post_service.add_comment(post_id, comment)


@router.delete("/{post_id}", response_model=dict)
def delete_post(post_id: str, user_id: str):
    """Deleta uma postagem (apenas o dono pode deletar)."""
    return post_service.delete_post(post_id, user_id)


@router.delete("/{post_id}/like", response_model=dict)
def remove_like(post_id: str, user_id: str):
    """Remove a curtida de um usuário em uma postagem."""
    return post_service.remove_like(post_id, user_id)


@router.delete("/{post_id}/comment/{comment_index}", response_model=dict)
def remove_comment(post_id: str, comment_index: int, user_id: str):
    """Remove um comentário específico (apenas o autor do comentário pode remover)."""
    return post_service.remove_comment(post_id, comment_index, user_id)
