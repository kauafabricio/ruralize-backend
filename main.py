from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.controllers.auth_controller import router as auth_router

app = FastAPI(
    title="Ruralize API",
    description="API para gerenciamento de ações sustentáveis na UFRPE",
    version="1.0.0"
)

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://ruralize-ufrpe.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/auth", tags=["Auth"])

@app.get("/")
def home():
    return {
        "name": "Ruralize API",
        "status": "online",
        "docs": "/docs",
        "version": "1.0.0"
    }