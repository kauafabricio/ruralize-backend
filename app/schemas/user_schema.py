from typing import Optional
from pydantic import BaseModel, EmailStr

# validar o cadastro
class UserCreate(BaseModel):
    name: str
    email: EmailStr # e-mail da ufrpe
    password: str
    registration: Optional[int] = None # matrícula (se for estudante)
    course: Optional[str] = None # curso (se for estudante)
    role: str  # "student" ou "teacher"

# validar o login
class UserLogin(BaseModel):
    email: EmailStr
    password: str