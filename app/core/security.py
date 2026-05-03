from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt

from app.core.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

# configuração do hash de senha
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# criptografa senha
def hash_password(password: str):
    return pwd_context.hash(password)


# verifica senha
def verify_password(password: str, hashed_password: str):
    return pwd_context.verify(password, hashed_password)


# cria token JWT
def create_token(data: dict):
    to_encode = data.copy()

    # define tempo de expiração
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})

    # gera token
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return token