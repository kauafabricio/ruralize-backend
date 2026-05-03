from fastapi import FastAPI
from app.controllers.auth_controller import router as auth_router

app = FastAPI()

# rota de autenticação
app.include_router(auth_router, prefix="/auth", tags=["Auth"])