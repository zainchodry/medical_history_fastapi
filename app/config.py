import os

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
ENV_PATH = os.path.join(BASE_DIR, ".env")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ENV_PATH, env_file_encoding="utf-8")

    # ── Project ──────────────────────────────────────────────
    PROJECT_NAME: str = "Medical History API"
    PROJECT_VERSION: str = "1.0.0"

    # ── Database ─────────────────────────────────────────────
    SQLALCHEMY_DATABASE_URL: str

    # ── Security / JWT ───────────────────────────────────────
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # ── Email (SMTP) ────────────────────────────────────────
    MAIL_USERNAME: str = ""
    MAIL_PASSWORD: str = ""
    MAIL_FROM: str = ""
    MAIL_PORT: int = 587
    MAIL_SERVER: str = "smtp.gmail.com"

    # ── Frontend ─────────────────────────────────────────────
    FRONTEND_URL: str = "http://localhost:3000"


settings = Settings()
