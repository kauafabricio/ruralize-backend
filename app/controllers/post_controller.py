from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Depends
from app.schemas.post_schema import PostCreate, PostUpdate, PostResponse, CommentCreate
from app.services.post_service import PostService
from app.services.sustainable_action_service import SustainableActionService
from app.repositories.post_repository import PostRepository
from app.repositories.profile_repository import ProfileRepository
from app.repositories.sustainable_action_repository import SustainableActionRepository
from app.database import db
from app.core.dependencies import get_current_user

router = APIRouter()

# instância do repositório e serviço de post
post_repo = PostRepository(db)
profile_repo = ProfileRepository(db)
action_repo = SustainableActionRepository(db)
action_service = SustainableActionService(action_repo)
post_service = PostService(post_repo, profile_repo, action_service)

# GET

@router.get("/", response_model=List[PostResponse])
def get_posts(user_id: Optional[str] = Query(None)):
    """Retorna todas as postagens, opcionalmente filtradas por usuário."""
    if user_id:
        return post_service.get_posts_by_user(user_id)
    return post_service.get_all_posts()

@router.get("/{post_id}", response_model=PostResponse)
def get_post(post_id: str):
    """Retorna uma única postagem por id."""
    return post_service.get_post(post_id)

# CREATE AND UPDATE

@router.post("/", response_model=dict)
def create_post(post: PostCreate, current_user: dict = Depends(get_current_user)):
    """Cria uma nova postagem para um usuário específico."""
    return post_service.create_post(post, current_user["id"])

@router.put("/{post_id}", response_model=dict)
def update_post(post_id: str, post: PostUpdate):
    """Atualiza campos de uma postagem existente."""
    return post_service.update_post(post_id, post)

# LIKE AND COMMENT

@router.post("/{post_id}/like", response_model=dict)
def like_post(post_id: str, current_user: dict = Depends(get_current_user)):
    """Registra um like e salva o id do usuário que curtiu."""
    return post_service.like_post(post_id, current_user["id"])

@router.post("/{post_id}/comment", response_model=dict)
def add_comment(post_id: str, comment: CommentCreate, current_user: dict = Depends(get_current_user)):
    """Adiciona um comentário à postagem com user_id e conteúdo."""
    # Usar o user_id do usuário autenticado
    comment_data = CommentCreate(user_id=current_user["id"], content=comment.content)
    return post_service.add_comment(post_id, comment_data)


# DELETE

@router.delete("/{post_id}", response_model=dict)
def delete_post(post_id: str, current_user: dict = Depends(get_current_user)):
    """Deleta uma postagem (apenas o dono pode deletar)."""
    return post_service.delete_post(post_id, current_user["id"])


@router.delete("/{post_id}/like", response_model=dict)
def remove_like(post_id: str, current_user: dict = Depends(get_current_user)):
    """Remove a curtida de um usuário em uma postagem."""
    return post_service.remove_like(post_id, current_user["id"])


@router.delete("/{post_id}/comment/{comment_index}", response_model=dict)
def remove_comment(post_id: str, comment_index: int, current_user: dict = Depends(get_current_user)):
    """Remove um comentário específico (apenas o autor do comentário pode remover)."""
    return post_service.remove_comment(post_id, comment_index, current_user["id"])
