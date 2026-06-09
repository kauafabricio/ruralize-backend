from typing import List
from fastapi import APIRouter, HTTPException
from app.schemas.sustainable_action_schema import SustainableActionCreate, SustainableActionUpdate, SustainableActionResponse
from app.services.sustainable_action_service import SustainableActionService, LEGACY_ACTION_MAPPING
from app.repositories.sustainable_action_repository import SustainableActionRepository
from app.repositories.post_repository import PostRepository
from app.database import db

router = APIRouter()

action_repo = SustainableActionRepository(db)
action_service = SustainableActionService(action_repo)
post_repo = PostRepository(db)


@router.get("/", response_model=List[SustainableActionResponse])
def get_actions():
    return action_service.get_all_actions()


@router.get("/{action_id}", response_model=SustainableActionResponse)
def get_action(action_id: str):
    return action_service.get_action(action_id)


@router.post("/", response_model=SustainableActionResponse)
def create_action(action: SustainableActionCreate, user_id: str):
    return action_service.create_action(action, user_id)


@router.put("/{action_id}", response_model=SustainableActionResponse)
def update_action(action_id: str, action: SustainableActionUpdate):
    return action_service.update_action(action_id, action)


@router.delete("/{action_id}", response_model=dict)
def delete_action(action_id: str):
    return action_service.delete_action(action_id)


@router.post("/init", response_model=dict)
def init_default_actions():
    return action_service.init_default_actions()


@router.post("/migrate", response_model=dict)
def migrate_posts():
    """Migra posts antigos que usam sustainable_action string para usar sustainable_action_id."""
    migrated_count = post_repo.migrate_posts_to_action_ids(LEGACY_ACTION_MAPPING)
    return {"message": f"{migrated_count} posts migrados com sucesso"}
