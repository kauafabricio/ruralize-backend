from typing import Optional, List
from pydantic import BaseModel, EmailStr

# validar o cadastro
class UserCreate(BaseModel):
    name: str
    email: EmailStr # e-mail da ufrpe
    password: str
    registration: Optional[str] = None # matrícula (se for estudante)
    course: Optional[str] = None # curso (se for estudante)
    department: Optional[str] = None # departamento (se for professor)
    role: str  # "student" ou "teacher"
    campus_location: Optional[str] = None # localização do campus
    description: Optional[str] = None # descrição do perfil
    profile_photo_url: Optional[str] = None # foto do perfil
    cover_photo_url: Optional[str] = None # foto da capa
    tags: Optional[List[str]] = [] # tags do perfil

# validar o login
class UserLogin(BaseModel):
    email: EmailStr
    password: str