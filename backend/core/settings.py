from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    ASYNC_DATABASE_URL: str = Field(..., description="Async database URL")
    SYNC_DATABASE_URL: str = Field(..., description="Sync database URL")

    # Celery
    CELERY_BROKER_URL: str = "amqp://guest:guest@rabbitmq:5672//"
    CELERY_RESULT_BACKEND: str = "rpc://"

    # Security
    SECRET_KEY: str = Field(..., min_length=1, description="Secret key for JWT")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS & Debug
    DEBUG: bool = False
    ALLOWED_HOSTS: List[str] = Field(default_factory=lambda: ["http://localhost:3000"])
    API_BASE_URL: str = Field("http://localhost:8000", description="Base URL for the API")

    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
        "extra": "ignore"
    }

    @field_validator('SECRET_KEY')
    @classmethod
    def secret_key_strength(cls, v: str) -> str:
        if len(v) < 2:
            raise ValueError("SECRET_KEY must be at least 32 characters long")
        if v in ["supersecret", "secret", "changeme", "your-secret-key"]:
            raise ValueError("Please use a strong, unique SECRET_KEY")
        return v

    @field_validator('ALLOWED_HOSTS')
    @classmethod
    def validate_hosts(cls, v: List[str]) -> List[str]:
        if not v:
            raise ValueError("ALLOWED_HOSTS cannot be empty")
        for host in v:
            if "*" in host:
                raise ValueError("Wildcard origins should be avoided")
        return v

    @field_validator('ASYNC_DATABASE_URL')
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        valid_prefixes = (
            'postgresql+asyncpg://',
            'sqlite+aiosqlite://',
            'mysql+aiomysql://'
        )
        if not v.startswith(valid_prefixes):
            raise ValueError(f"Invalid async database URL format. Must start with: {valid_prefixes}")
        return v

    @property
    def database_url(self) -> str:
        return self.ASYNC_DATABASE_URL

    @property
    def is_production(self) -> bool:
        return not self.DEBUG

    @property
    def cors_origins(self) -> List[str]:
        if self.DEBUG:
            return ["*"]  # Only in debug mode
        return self.ALLOWED_HOSTS


settings = Settings()
