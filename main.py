from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.controllers.auth_controller import router as auth_router

app = FastAPI()

# 🔥 CONFIGURAÇÃO CORS
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # pode usar ["*"] pra testar
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# rota de autenticação
app.include_router(auth_router, prefix="/auth", tags=["Auth"])

@app.get("/")
def home():
    return {"message": "API rodando"}