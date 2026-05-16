from typing import List
from fastapi import APIRouter, HTTPException
from app.schemas.post_schema import PostCreate, PostUpdate, PostResponse, CommentCreate
from app.services.post_service import PostService
from app.repositories.post_repository import PostRepository
from app.database import db

router = APIRouter()

# instância do repositório e serviço de post
post_repo = PostRepository(db)
post_service = PostService(post_repo)

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
