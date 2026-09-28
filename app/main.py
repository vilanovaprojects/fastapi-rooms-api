from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import init_db
from app.routes.sala_routes import router as sala_router

app = FastAPI(
    title="API Gestión de Salas",
    description="API REST para gestionar salas educativas",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()

app.include_router(sala_router)


@app.get("/")
def root():
    return {"mensaje": "Bienvenido a la API de Gestión de Salas"}


@app.get("/health")
def health_check():
    return {"status": "ok"}
