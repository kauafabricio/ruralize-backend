from fastapi import HTTPException
from app.repositories.sustainable_action_repository import SustainableActionRepository
from app.schemas.sustainable_action_schema import SustainableActionCreate, SustainableActionUpdate
from datetime import datetime


DEFAULT_ACTIONS = [
    {"id": "tree-planting", "name": "Plantio de Árvores", "icon": "🌱"},
    {"id": "recycling", "name": "Reciclagem", "icon": "♻️"},
    {"id": "water-conservation", "name": "Conservação de Água", "icon": "💧"},
    {"id": "energy-efficiency", "name": "Eficiência Energética", "icon": "⚡"},
    {"id": "composting", "name": "Compostagem", "icon": "🌿"},
    {"id": "biodiversity", "name": "Biodiversidade", "icon": "🦋"},
    {"id": "sustainable-agriculture", "name": "Agricultura Sustentável", "icon": "🌾"},
    {"id": "clean-energy", "name": "Energia Limpa", "icon": "☀️"},
    {"id": "pollution-reduction", "name": "Redução de Poluição", "icon": "🌍"},
    {"id": "education", "name": "Educação Ambiental", "icon": "📚"},
]

LEGACY_ACTION_MAPPING = {
    "general": "tree-planting",
    "events": "tree-planting",
    "warnings": "pollution-reduction",
    "projects": "sustainable-agriculture",
}


class SustainableActionService:

    def __init__(self, action_repo: SustainableActionRepository):
        self.action_repo = action_repo

    def init_default_actions(self):
        for action in DEFAULT_ACTIONS:
            if not self.action_repo.action_exists(action["id"]):
                action_data = {
                    "id": action["id"],
                    "name": action["name"],
                    "icon": action["icon"],
                    "is_default": True,
                    "created_by": None
                }
                self.action_repo.create_action(action_data)
        return {"message": "Ações padrão inicializadas com sucesso"}

    def get_all_actions(self):
        return self.action_repo.get_all_actions()

    def get_action(self, action_id: str):
        action = self.action_repo.get_action_by_id(action_id)
        if not action:
            raise HTTPException(status_code=404, detail="Ação não encontrada")
        return action

    def create_action(self, action_data: SustainableActionCreate, user_id: str):
        action_id = self._generate_action_id(action_data.name)

        if self.action_repo.action_exists(action_id):
            raise HTTPException(status_code=400, detail="Ação com este nome já existe")

        payload = {
            "id": action_id,
            "name": action_data.name,
            "icon": action_data.icon or "🌱",
            "is_default": False,
            "created_by": user_id
        }
        self.action_repo.create_action(payload)
        return self.action_repo.get_action_by_id(action_id)

    def update_action(self, action_id: str, action_data: SustainableActionUpdate):
        if not self.action_repo.action_exists(action_id):
            raise HTTPException(status_code=404, detail="Ação não encontrada")

        update_payload = {k: v for k, v in action_data.dict().items() if v is not None}
        if not update_payload:
            raise HTTPException(status_code=400, detail="Nenhum campo para atualizar")

        result = self.action_repo.update_action(action_id, update_payload)
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Ação não encontrada")

        return self.action_repo.get_action_by_id(action_id)

    def delete_action(self, action_id: str):
        if self.action_repo.action_exists(action_id):
            result = self.action_repo.delete_action(action_id)
            if result.deleted_count > 0:
                return {"message": "Ação deletada com sucesso"}

        raise HTTPException(status_code=404, detail="Ação não encontrada")

    def validate_action_exists(self, action_id: str):
        return self.action_repo.action_exists(action_id)

    def resolve_action_id(self, action_id: str = None, action_name: str = None):
        if action_id:
            if self.validate_action_exists(action_id):
                return action_id
            else:
                raise HTTPException(status_code=400, detail=f"Ação com ID '{action_id}' não encontrada")

        if action_name:
            mapped_id = LEGACY_ACTION_MAPPING.get(action_name)
            if mapped_id:
                return mapped_id

            action = self.action_repo.get_action_by_name(action_name)
            if action:
                return action["id"]

            return LEGACY_ACTION_MAPPING.get("general", "tree-planting")

        return None

    def _generate_action_id(self, name: str):
        return name.lower().strip().replace(" ", "-")
