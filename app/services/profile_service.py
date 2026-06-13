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

    def follow_user(self, user_id: str, target_user_id: str):
        if user_id == target_user_id:
            raise HTTPException(status_code=400, detail="Não é possível seguir a si mesmo")

        current_user = self.profile_repo.find_raw_by_user_id(user_id)
        target_user = self.profile_repo.find_raw_by_user_id(target_user_id)

        if not current_user or not target_user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")

        if str(target_user_id) in [str(item) for item in current_user.get("following", [])]:
            return {"message": "Você já segue este usuário"}

        self.profile_repo.add_following(user_id, target_user_id)
        self.profile_repo.add_follower(target_user_id, user_id)

        return {"message": "Usuário seguido com sucesso"}

    def unfollow_user(self, user_id: str, target_user_id: str):
        if user_id == target_user_id:
            raise HTTPException(status_code=400, detail="Não é possível deixar de seguir a si mesmo")

        current_user = self.profile_repo.find_raw_by_user_id(user_id)
        target_user = self.profile_repo.find_raw_by_user_id(target_user_id)

        if not current_user or not target_user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")

        if str(target_user_id) not in [str(item) for item in current_user.get("following", [])]:
            return {"message": "Você não segue este usuário"}

        self.profile_repo.remove_following(user_id, target_user_id)
        self.profile_repo.remove_follower(target_user_id, user_id)

        return {"message": "Usuário deixou de ser seguido"}

    def get_follow_status(self, user_id: str, target_user_id: str):
        current_user = self.profile_repo.find_raw_by_user_id(user_id)
        if not current_user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")

        is_following = str(target_user_id) in [str(item) for item in current_user.get("following", [])]
        return {"is_following": is_following}

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

    def get_following(self, user_id: str):
        user = self.profile_repo.find_raw_by_user_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")

        following_ids = [str(item) for item in user.get("following", [])]
        return self.profile_repo.get_users_by_ids(following_ids)

    def get_followers(self, user_id: str):
        user = self.profile_repo.find_raw_by_user_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")

        follower_ids = [str(item) for item in user.get("followers", [])]
        return self.profile_repo.get_users_by_ids(follower_ids)
