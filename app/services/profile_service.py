from fastapi import HTTPException
from app.repositories.profile_repository import ProfileRepository
from app.schemas.profile_schema import ProfileUpdate


class ProfileService:

    def __init__(self, profile_repo: ProfileRepository):
        self.profile_repo = profile_repo

    def get_profile_by_user_id(self, user_id: str):
        profile = self.profile_repo.find_by_user_id(user_id)
        if not profile:
            raise HTTPException(status_code=404, detail="Perfil não encontrado")
        return profile

    def get_profile_by_id(self, profile_id: str):
        profile = self.profile_repo.find_by_id(profile_id)
        if not profile:
            raise HTTPException(status_code=404, detail="Perfil não encontrado")
        return profile

    def get_all_profiles(self):
        return self.profile_repo.get_all_profiles()

    def update_profile(self, user_id: str, profile_data: ProfileUpdate):
        update_payload = {k: v for k, v in profile_data.dict().items() if v is not None}
        if not update_payload:
            raise HTTPException(status_code=400, detail="Nenhum campo para atualizar")

        result = self.profile_repo.update_by_user_id(user_id, update_payload)
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Perfil não encontrado")

        return {"message": "Perfil atualizado com sucesso"}

    def search_profiles_by_name(self, name: str):
        if not name or len(name.strip()) < 2:
            raise HTTPException(status_code=400, detail="Nome deve ter pelo menos 2 caracteres")
        return self.profile_repo.find_by_name(name)

    def search_profiles_by_course(self, course: str):
        return self.profile_repo.find_by_course(course)

    def search_profiles_by_department(self, department: str):
        return self.profile_repo.find_by_department(department)

    def search_profiles_by_role(self, role: str):
        if role not in ["student", "teacher"]:
            raise HTTPException(status_code=400, detail="Role inválido")
        return self.profile_repo.find_by_role(role)

    def search_profiles_by_tags(self, tags: list):
        if not tags:
            raise HTTPException(status_code=400, detail="Tags obrigatórias")
        return self.profile_repo.find_by_tags(tags)
