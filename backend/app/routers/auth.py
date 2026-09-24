"""Endpoint de autenticação (login com usuário demo)."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import create_access_token, verify_password
from app.db.session import get_db
from app.models.models import User
from app.schemas.schemas import LoginRequest, TokenResponse

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Autentica um usuário e retorna um token JWT",
    description=(
        "Recebe e-mail e senha e retorna um token de acesso Bearer. "
        "Use as credenciais demo definidas em `.env.example` para testar."
    ),
)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    user = db.query(User).filter(User.email == payload.email).first()
    if user is None or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="E-mail ou senha inválidos"
        )
    token = create_access_token(subject=user.email)
    return TokenResponse(access_token=token)
