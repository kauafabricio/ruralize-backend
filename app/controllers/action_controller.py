from typing import List
from fastapi import APIRouter, HTTPException
from app.schemas.action_schema import ActionCreate, ActionUpdate, ActionResponse
from app.services.action_service import ActionService
from app.repositories.action_repository import ActionRepository
from app.database import db

router = APIRouter()

action_repo = ActionRepository(db)
action_service = ActionService(action_repo)


@router.get("/", response_model=List[ActionResponse])
def get_actions():
    """List all sustainability actions."""
    return action_service.get_all_actions()


@router.get("/{action_id}", response_model=ActionResponse)
def get_action(action_id: str):
    """Get a single action by ID."""
    return action_service.get_action(action_id)


@router.post("/", response_model=dict)
def create_action(action: ActionCreate):
    """Create a new sustainability action."""
    return action_service.create_action(action)


@router.put("/{action_id}", response_model=dict)
def update_action(action_id: str, action: ActionUpdate):
    """Update an existing action."""
    return action_service.update_action(action_id, action)


@router.delete("/{action_id}", response_model=dict)
def delete_action(action_id: str):
    """Delete an action."""
    return action_service.delete_action(action_id)
