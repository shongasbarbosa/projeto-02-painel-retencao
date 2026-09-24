"""Ponto de entrada da aplicação FastAPI."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routers import auth, courses, enrollments, reports, students
from app.schemas.schemas import HealthOut

app = FastAPI(
    title="Painel de Retenção API",
    description=(
        "API para identificar alunos em risco de evasão, priorizar contatos "
        "de tutoria e comparar turmas em uma plataforma de EaD."
    ),
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(courses.router)
app.include_router(enrollments.router)
app.include_router(reports.router)
app.include_router(students.router)


@app.get("/health", response_model=HealthOut, tags=["health"], summary="Verifica a saúde da API")
def health() -> HealthOut:
    return HealthOut()
