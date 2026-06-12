from pydantic import BaseModel
from typing import Optional, List


class ProfileCreate(BaseModel):
    description: Optional[str] = None
    profile_photo_url: Optional[str] = None
    cover_photo_url: Optional[str] = None


class ProfileUpdate(BaseModel):
    description: Optional[str] = None
    profile_photo_url: Optional[str] = None
    cover_photo_url: Optional[str] = None


class ProfileAcademicInfo(BaseModel):
    email: str
    registration: Optional[str] = None
    campus_location: Optional[str] = None


class ProfileResponse(BaseModel):
    id: str
    name: str
    role: str
    course: Optional[str] = None
    department: Optional[str] = None
    description: Optional[str] = None
    profile_photo_url: Optional[str] = None
    cover_photo_url: Optional[str] = None
    academic_info: Optional[ProfileAcademicInfo] = None


class UserProfileResponse(BaseModel):
    id: str
    name: str
    role: str
    course: Optional[str] = None
    department: Optional[str] = None
    profile_photo_url: Optional[str] = None
    description: Optional[str] = None
