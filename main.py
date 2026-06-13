from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.controllers.auth_controller import router as auth_router
from app.controllers.feed_controller import router as feed_router
from app.controllers.post_controller import router as post_router
from app.controllers.profile_controller import router as profile_router
from app.controllers.action_controller import router as action_router
from app.controllers.event_controller import router as event_router
from app.controllers.subscription_controller import router as subscription_router
from app.controllers.reward_controller import router as reward_router
from pymongo.errors import PyMongoError, ServerSelectionTimeoutError

app = FastAPI(
    title="Ruralize API",
    description="API para gerenciamento de ações sustentáveis na UFRPE",
    version="1.0.0"
)

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3001",
    "http://localhost:3002",
    "http://127.0.0.1:3002",
    "https://ruralize-ufrpe.vercel.app",
    "https://ruralize-bnamd1cew-kauas-projects-24d9238d.vercel.app",
    "https://ruralize-git-dev-kauas-projects-24d9238d.vercel.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(ServerSelectionTimeoutError)
async def mongo_timeout_exception_handler(request: Request, exc: ServerSelectionTimeoutError):
    return JSONResponse(
        status_code=503,
        content={
            "detail": "MongoDB indisponível: verifique se o serviço do MongoDB está em execução e acessível.",
        },
    )

@app.exception_handler(PyMongoError)
async def mongo_exception_handler(request: Request, exc: PyMongoError):
    return JSONResponse(
        status_code=503,
        content={
            "detail": "Serviço de banco de dados indisponível. Verifique se o MongoDB está em execução e se a configuração do MONGO_URL está correta.",
        },
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    if isinstance(exc, HTTPException):
        raise exc
    return JSONResponse(
        status_code=500,
        content={"detail": "Ocorreu um erro interno no servidor."},
    )

app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(feed_router, prefix="/feed", tags=["Feed"])
app.include_router(post_router, prefix="/posts", tags=["Posts"])
app.include_router(profile_router, prefix="/profiles", tags=["Profiles"])
app.include_router(action_router, prefix="/actions", tags=["Actions"])
app.include_router(event_router, prefix="/events", tags=["Events"])
app.include_router(subscription_router, prefix="/events", tags=["Subscriptions"])
app.include_router(reward_router, prefix="/rewards", tags=["Rewards"])

@app.get("/")
def home():
    return {
        "name": "Ruralize API",
        "status": "online",
        "docs": "/docs",
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
