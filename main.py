from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.controllers.auth_controller import router as auth_router
from app.controllers.feed_controller import router as feed_router
from app.controllers.post_controller import router as post_router
from app.controllers.profile_controller import router as profile_router

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
app.include_router(feed_router, prefix="/feed", tags=["Feed"])
app.include_router(post_router, prefix="/posts", tags=["Posts"])
app.include_router(profile_router, prefix="/profiles", tags=["Profiles"])

@app.get("/")
def home():
    return {
        "name": "Ruralize API",
        "status": "online",
        "docs": "/docs",
        "version": "1.0.0"
    }