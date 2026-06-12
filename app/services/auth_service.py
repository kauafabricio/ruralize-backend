from datetime import datetime
from app.core.security import hash_password, verify_password, create_token
from fastapi import HTTPException

# serviço de autenticação (US001, US002 e US003)
class AuthService:

    def __init__(self, user_repo):
        self.user_repo = user_repo

    # cadastro (US001)
    def register(self, user):

        # evitar duplicidade de email
        email = user.email.lower()

        # verifica se email já existe
        existing_user = self.user_repo.find_by_email(email)
        if existing_user:
            raise HTTPException(status_code=400, detail="Usuário com e-mail já cadastrado")

        # estudante já cadastrado
        if user.role == "student":
            if not user.registration:
                raise HTTPException(status_code=400, detail="Matrícula é obrigatória para discentes")
            if not user.course or not user.course.strip():
                raise HTTPException(status_code=400, detail="Curso é obrigatório para discentes")

            existing_student = self.user_repo.find_by_registration(user.registration)
            if existing_student:
                raise HTTPException(status_code=400, detail="Essa matrícula já foi cadastrada")

        # validação de campos específicos por role
        if user.role == "teacher":
            if not user.department or not user.department.strip():
                raise HTTPException(status_code=400, detail="Departamento é obrigatório para docentes")

        # validação campus_location para ambos
        if not user.campus_location or not user.campus_location.strip():
            raise HTTPException(status_code=400, detail="Localização do campus é obrigatória")

        # transforma objeto em dicionário
        user_dict = user.dict()

        # salva email correto
        user_dict["email"] = email

        # criptografa senha para salvar no bd
        user_dict["password"] = hash_password(user.password)

        # adiciona data de criação
        user_dict["created_at"] = datetime.utcnow()

        # salva no banco
        result = self.user_repo.create_user(user_dict)

        return {
            "message": "Usuário criado com sucesso",
            "user_id": str(result.inserted_id)
        }


    # LOGIN (US002)
    def login(self, user):

        # busca usuário no banco
        db_user = self.user_repo.find_by_email(user.email)

        # valida se existe
        if not db_user:
            raise HTTPException(status_code=400, detail="Credenciais inválidas")

        # valida senha
        if not verify_password(user.password, db_user["password"]):
            raise HTTPException(status_code=400, detail="Credenciais inválidas")

        # gera token JWT
        token = create_token({
            "user_id": str(db_user["_id"])
        })

        return {"access_token": token}

    # Verifica campos obrigatórios faltantes no perfil
    def get_missing_profile_fields(self, user_id: str):
        from bson import ObjectId

        user = self.user_repo.find_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")

        missing_fields = []
        role = user.get("role", "student")

        # Campos obrigatórios para ambos
        if not user.get("description"):
            missing_fields.append("description")

        if not user.get("campus_location"):
            missing_fields.append("campus_location")

        # Campos específicos por role
        if role == "teacher":
            if not user.get("department"):
                missing_fields.append("department")

        # Campos opcionais (mas recomendados)
        optional_fields = []
        if not user.get("profile_photo_url"):
            optional_fields.append("profile_photo_url")
        if not user.get("cover_photo_url"):
            optional_fields.append("cover_photo_url")

        return {
            "completed": len(missing_fields) == 0,
            "missing_fields": missing_fields,
            "required_fields": missing_fields,
            "optional_fields": optional_fields
        }