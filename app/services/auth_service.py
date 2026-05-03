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
            return {"error": "Usuário com e-mail já cadastrado"}
        
        # estudante já cadastrado
        if user.role == "student":
            if not user.registration:
                raise HTTPException(status_code=400, detail="Matrícula é obrigatória para discentes")
            
            if not user.course:
                raise HTTPException(status_code=400, detail="Curso é obrigatório para discentes")

            existing_student = self.user_repo.find_by_registration(user.registration)
            if existing_student:
                raise HTTPException(status_code=400, detail="Essa matrícula já foi cadastrada")

        # transforma objeto em dicionário
        user_dict = user.dict()

        # salva email correto
        user_dict["email"] = email

        # criptografa senha para salvar no bd
        user_dict["password"] = hash_password(user.password)

        # adiciona data de criação
        user_dict["created_at"] = datetime.utcnow()

        # salva no banco
        self.user_repo.create_user(user_dict)

        return {"message": "Usuário criado com sucesso"}


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