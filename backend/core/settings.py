from pydantic import BaseSettings

class Settings(BaseSettings):
    # POSTGRES_USER: str = "xerottin"
    # POSTGRES_PASSWORD: str = "1111"
    # POSTGRES_DB: str = "coffe_shop"
    # POSTGRES_HOST: str = "localhost"
    # POSTGRES_PORT: str = "5432"
    ASYNC_DATABASE_URL: str
    SYNC_DATABASE_URL: str

    SECRET_KEY: str = "supersecret"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"

    @property
    def database_url(self):
        return self.ASYNC_DATABASE_URL
    # @property
    # def database_url(self):
    #     return (
    #         f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
    #         f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    #     )

settings = Settings()


