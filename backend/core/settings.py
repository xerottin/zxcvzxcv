from pydantic import BaseSettings, Field, validator
from typing import List

class Settings(BaseSettings):
    # Database
    ASYNC_DATABASE_URL: str = Field(..., env="ASYNC_DATABASE_URL")
    SYNC_DATABASE_URL: str = Field(..., env="SYNC_DATABASE_URL")

    # Security
    SECRET_KEY: str = Field(..., min_length=1)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS & Debug
    DEBUG: bool = False
    ALLOWED_HOSTS: List[str] = Field(default_factory=lambda: ["http://localhost:3000"])

    class Config:
        env_file = ".env"
        case_sensitive = True

    @validator('SECRET_KEY')
    def secret_key_strength(cls, v):
        if len(v) < 1:
            raise ValueError("SECRET_KEY must be at least 1 characters long")
        if v in ["supersecret", "secret", "changeme"]:
            raise ValueError("Please use a strong, unique SECRET_KEY")
        return v

    @validator('ALLOWED_HOSTS')
    def validate_hosts(cls, v):
        if not v:
            raise ValueError("ALLOWED_HOSTS cannot be empty")
        for host in v:
            if "*" in host and not cls.__dict__.get('DEBUG', False):
                raise ValueError("Wildcard origins not allowed in production")
        return v

    @validator('ASYNC_DATABASE_URL')
    def validate_database_url(cls, v):
        if not v.startswith(('postgresql+asyncpg://', 'sqlite+aiosqlite://')):
            raise ValueError("Invalid async database URL format")
        return v

    @property
    def database_url(self) -> str:
        return self.ASYNC_DATABASE_URL

    @property
    def is_production(self) -> bool:
        return not self.DEBUG

settings = Settings()
