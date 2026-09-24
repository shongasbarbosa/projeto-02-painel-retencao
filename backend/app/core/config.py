"""Configurações da aplicação, carregadas de variáveis de ambiente."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/painel_retencao"
    jwt_secret: str = "change-me"
    jwt_algorithm: str = "HS256"
    jwt_expires_minutes: int = 60 * 8

    demo_user_email: str = "demo@painelretencao.com"
    demo_user_password: str = "demo123456"

    cors_origins: list[str] = ["http://localhost:8080", "http://localhost:5173"]


settings = Settings()
