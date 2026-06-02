from fastapi import HTTPException
from app.repositories.action_repository import ActionRepository
from app.schemas.action_schema import ActionCreate, ActionUpdate


class ActionService:

    def __init__(self, action_repo: ActionRepository):
        self.action_repo = action_repo

    def get_all_actions(self):
        return self.action_repo.get_all_actions()

    def get_action(self, action_id: str):
        action = self.action_repo.get_action_by_id(action_id)
        if not action:
            raise HTTPException(status_code=404, detail="Ação não encontrada")
        return action

    def create_action(self, action_data: ActionCreate):
        payload = action_data.dict()
        action_id = self.action_repo.create_action(payload)
        return {"message": "Ação criada com sucesso", "id": action_id}

    def update_action(self, action_id: str, action_data: ActionUpdate):
        update_payload = {k: v for k, v in action_data.dict().items() if v is not None}
        if not update_payload:
            raise HTTPException(status_code=400, detail="Nenhum campo para atualizar")

        result = self.action_repo.update_action(action_id, update_payload)
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Ação não encontrada")

        return {"message": "Ação atualizada com sucesso"}

    def delete_action(self, action_id: str):
        result = self.action_repo.delete_action(action_id)
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Ação não encontrada")

        return {"message": "Ação deletada com sucesso"}
