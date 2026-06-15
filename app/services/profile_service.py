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

    def follow_user(self, user_id: str, target_id: str):
        if user_id == target_id:
            raise HTTPException(status_code=400, detail="Não é possível seguir a si mesmo")

        if not self.profile_repo.find_by_user_id(user_id):
            raise HTTPException(status_code=404, detail="Perfil do usuário não encontrado")

        if not self.profile_repo.find_by_user_id(target_id):
            raise HTTPException(status_code=404, detail="Usuário alvo não encontrado")

        self.profile_repo.add_follow(user_id, target_id)
        self.profile_repo.add_follower(target_id, user_id)

        return {"message": "Seguindo usuário com sucesso"}

    def unfollow_user(self, user_id: str, target_id: str):
        if user_id == target_id:
            raise HTTPException(status_code=400, detail="Não é possível deixar de seguir a si mesmo")

        if not self.profile_repo.find_by_user_id(user_id):
            raise HTTPException(status_code=404, detail="Perfil do usuário não encontrado")

        if not self.profile_repo.find_by_user_id(target_id):
            raise HTTPException(status_code=404, detail="Usuário alvo não encontrado")

        self.profile_repo.remove_follow(user_id, target_id)
        self.profile_repo.remove_follower(target_id, user_id)

        return {"message": "Deixou de seguir o usuário com sucesso"}

    def get_following_profiles(self, user_id: str):
        following_ids = self.profile_repo.get_following_ids(user_id)
        if following_ids is None:
            raise HTTPException(status_code=404, detail="Perfil não encontrado")
        return self.profile_repo.find_by_user_ids(following_ids)

    def get_followers_profiles(self, user_id: str):
        follower_ids = self.profile_repo.get_followers_ids(user_id)
        if follower_ids is None:
            raise HTTPException(status_code=404, detail="Perfil não encontrado")
        return self.profile_repo.find_by_user_ids(follower_ids)

    def get_follow_status(self, user_id: str, target_id: str):
        if not self.profile_repo.find_by_user_id(user_id):
            raise HTTPException(status_code=404, detail="Perfil do usuário não encontrado")

        if not self.profile_repo.find_by_user_id(target_id):
            raise HTTPException(status_code=404, detail="Usuário alvo não encontrado")

        return {"is_following": self.profile_repo.is_following(user_id, target_id)}

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
