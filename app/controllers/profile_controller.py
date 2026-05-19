from typing import List
from fastapi import APIRouter, HTTPException, Query
from app.schemas.profile_schema import ProfileUpdate, ProfileResponse, UserProfileResponse
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
            description=p.get("description"),
            tags=p.get("tags", [])
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
            description=p.get("description"),
            tags=p.get("tags", [])
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
            description=p.get("description"),
            tags=p.get("tags", [])
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
            description=p.get("description"),
            tags=p.get("tags", [])
        )
        for p in profiles
    ]


@router.get("/search/by-tags", response_model=List[UserProfileResponse])
def search_by_tags(tags: List[str] = Query(...)):
    """Busca perfis por tags."""
    profiles = profile_service.search_profiles_by_tags(tags)
    return [
        UserProfileResponse(
            id=p["id"],
            name=p["name"],
            role=p["role"],
            course=p.get("course"),
            department=p.get("department"),
            profile_photo_url=p.get("profile_photo_url"),
            description=p.get("description"),
            tags=p.get("tags", [])
        )
        for p in profiles
    ]


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
            description=p.get("description"),
            tags=p.get("tags", [])
        )
        for p in profiles
    ]


@router.get("/{profile_id}", response_model=UserProfileResponse)
def get_profile(profile_id: str):
    """Retorna informações públicas de um perfil."""
    profile = profile_service.get_profile_by_id(profile_id)
    return UserProfileResponse(
        id=profile["id"],
        name=profile["name"],
        role=profile["role"],
        course=profile.get("course"),
        department=profile.get("department"),
        profile_photo_url=profile.get("profile_photo_url"),
        description=profile.get("description"),
        tags=profile.get("tags", [])
    )
