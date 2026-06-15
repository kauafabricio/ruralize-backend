from typing import List
from fastapi import APIRouter, HTTPException, Query
from app.schemas.profile_schema import (
    ProfileUpdate,
    ProfileResponse,
    UserProfileResponse,
    FollowStatusResponse,
)
from app.services.profile_service import ProfileService
from app.repositories.profile_repository import ProfileRepository
from app.database import db

router = APIRouter()

profile_repo = ProfileRepository(db)
profile_service = ProfileService(profile_repo)


@router.get("/user/{user_id}", response_model=ProfileResponse)
def get_profile_by_user(user_id: str):
    """Retorna o perfil completo de um usuário."""
    return profile_service.get_profile_by_user_id(user_id)


@router.put("/user/{user_id}", response_model=dict)
def update_profile(user_id: str, profile_data: ProfileUpdate):
    """Atualiza o perfil do usuário logado."""
    return profile_service.update_profile(user_id, profile_data)


@router.get("/search/by-name", response_model=List[UserProfileResponse])
def search_by_name(name: str = Query(..., min_length=2)):
    """Busca perfis por nome."""
    profiles = profile_service.search_profiles_by_name(name)
    return [
        UserProfileResponse(
            id=p["id"],
            name=p["name"],
            role=p["role"],
            course=p.get("course"),
            department=p.get("department"),
            profile_photo_url=p.get("profile_photo_url"),
            description=p.get("description")
        )
        for p in profiles
    ]


@router.get("/search/by-course", response_model=List[UserProfileResponse])
def search_by_course(course: str):
    """Busca perfis por curso."""
    profiles = profile_service.search_profiles_by_course(course)
    return [
        UserProfileResponse(
            id=p["id"],
            name=p["name"],
            role=p["role"],
            course=p.get("course"),
            department=p.get("department"),
            profile_photo_url=p.get("profile_photo_url"),
            description=p.get("description")
        )
        for p in profiles
    ]


@router.get("/search/by-department", response_model=List[UserProfileResponse])
def search_by_department(department: str):
    """Busca perfis por departamento."""
    profiles = profile_service.search_profiles_by_department(department)
    return [
        UserProfileResponse(
            id=p["id"],
            name=p["name"],
            role=p["role"],
            course=p.get("course"),
            department=p.get("department"),
            profile_photo_url=p.get("profile_photo_url"),
            description=p.get("description")
        )
        for p in profiles
    ]


@router.get("/search/by-role/{role}", response_model=List[UserProfileResponse])
def search_by_role(role: str):
    """Busca perfis por role (student ou teacher)."""
    profiles = profile_service.search_profiles_by_role(role)
    return [
        UserProfileResponse(
            id=p["id"],
            name=p["name"],
            role=p["role"],
            course=p.get("course"),
            department=p.get("department"),
            profile_photo_url=p.get("profile_photo_url"),
            description=p.get("description")
        )
        for p in profiles
    ]


@router.post("/user/{user_id}/follow", response_model=dict)
def follow_user(user_id: str, target_id: str = Query(..., alias="target_id")):
    """Seguir outro usuário."""
    return profile_service.follow_user(user_id, target_id)


@router.delete("/user/{user_id}/follow", response_model=dict)
def unfollow_user(user_id: str, target_id: str = Query(..., alias="target_id")):
    """Deixar de seguir outro usuário."""
    return profile_service.unfollow_user(user_id, target_id)


@router.get("/user/{user_id}/following", response_model=List[UserProfileResponse])
def get_following(user_id: str):
    """Retorna os perfis que o usuário está seguindo."""
    profiles = profile_service.get_following_profiles(user_id)
    return [
        UserProfileResponse(
            id=p["id"],
            name=p["name"],
            role=p["role"],
            course=p.get("course"),
            department=p.get("department"),
            profile_photo_url=p.get("profile_photo_url"),
            description=p.get("description")
        )
        for p in profiles
    ]


@router.get("/user/{user_id}/followers", response_model=List[UserProfileResponse])
def get_followers(user_id: str):
    """Retorna os perfis que seguem o usuário."""
    profiles = profile_service.get_followers_profiles(user_id)
    return [
        UserProfileResponse(
            id=p["id"],
            name=p["name"],
            role=p["role"],
            course=p.get("course"),
            department=p.get("department"),
            profile_photo_url=p.get("profile_photo_url"),
            description=p.get("description")
        )
        for p in profiles
    ]


@router.get("/user/{user_id}/follow-status", response_model=FollowStatusResponse)
def get_follow_status(user_id: str, target_id: str = Query(..., alias="target_id")):
    """Retorna se o usuário está seguindo outro usuário."""
    return profile_service.get_follow_status(user_id, target_id)


@router.get("/", response_model=List[UserProfileResponse])
def get_all_profiles():
    """Retorna todos os perfis (informações públicas)."""
    profiles = profile_service.get_all_profiles()
    return [
        UserProfileResponse(
            id=p["id"],
            name=p["name"],
            role=p["role"],
            course=p.get("course"),
            department=p.get("department"),
            profile_photo_url=p.get("profile_photo_url"),
            description=p.get("description")
        )
        for p in profiles
    ]
