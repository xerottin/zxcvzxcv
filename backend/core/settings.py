from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    ASYNC_DATABASE_URL: str = Field(..., description="Async database URL")
    SYNC_DATABASE_URL: str = Field(..., description="Sync database URL")

    SECRET_KEY: str = Field(..., min_length=1, description="Secret key for JWT")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    DEBUG: bool = False
    ALLOWED_HOSTS: List[str] = Field(default_factory=lambda: ["http://localhost:3000"])

    STRIPE_SECRET_KEY: str = Field(..., description="Stripe secret key")
    STRIPE_PUBLISHABLE_KEY: str = Field(..., description="Stripe publishable key")
    STRIPE_WEBHOOK_SECRET: str = Field(..., description="Stripe webhook secret")
    STRIPE_SUCCESS_URL: str = Field(
        default="http://localhost:3000/payment/success",
        description="URL to redirect after successful payment"
    )
    STRIPE_CANCEL_URL: str = Field(
        default="http://localhost:3000/payment/cancel", 
        description="URL to redirect after cancelled payment"
    )
    STRIPE_CURRENCY: str = Field(
        default="USD",
        description="Default currency for payments"
    )

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
            'postgresql+asyncpg://'
        )
        if not v.startswith(valid_prefixes):
            raise ValueError(f"Invalid async database URL format. Must start with: {valid_prefixes}")
        return v

    @field_validator('STRIPE_SECRET_KEY')
    @classmethod
    def validate_stripe_secret_key(cls, v: str) -> str:
        if not v.startswith(('sk_test_', 'sk_live_')):
            raise ValueError("STRIPE_SECRET_KEY must start with 'sk_test_' or 'sk_live_'")
        if len(v) < 20:
            raise ValueError("STRIPE_SECRET_KEY appears to be invalid (too short)")
        return v

    @field_validator('STRIPE_PUBLISHABLE_KEY')
    @classmethod
    def validate_stripe_publishable_key(cls, v: str) -> str:
        if not v.startswith(('pk_test_', 'pk_live_')):
            raise ValueError("STRIPE_PUBLISHABLE_KEY must start with 'pk_test_' or 'pk_live_'")
        if len(v) < 10:
            raise ValueError("STRIPE_PUBLISHABLE_KEY appears to be invalid (too short)")
        return v

    @field_validator('STRIPE_WEBHOOK_SECRET')
    @classmethod
    def validate_stripe_webhook_secret(cls, v: str) -> str:
        if not v.startswith('whsec_'):
            raise ValueError("STRIPE_WEBHOOK_SECRET must start with 'whsec_'")
        return v

    @field_validator('STRIPE_CURRENCY')
    @classmethod
    def validate_currency(cls, v: str) -> str:
        # Common currencies supported by Stripe
        supported_currencies = [
            'USD', 'EUR', "UZS"
        ]
        v_upper = v.upper()
        if v_upper not in supported_currencies:
            raise ValueError(f"Currency {v} is not supported. Supported currencies: {', '.join(supported_currencies[:10])}...")
        return v_upper

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

    @property
    def is_stripe_live_mode(self) -> bool:
        return self.STRIPE_SECRET_KEY.startswith('sk_live_')

    @property
    def stripe_keys_match_env(self) -> bool:
        secret_is_live = self.STRIPE_SECRET_KEY.startswith('sk_live_')
        publishable_is_live = self.STRIPE_PUBLISHABLE_KEY.startswith('pk_live_')
        return secret_is_live == publishable_is_live


settings = Settings()

