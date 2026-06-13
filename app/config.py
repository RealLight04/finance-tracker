from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Finance Tracker API"
    database_url: str = "sqlite:///./finance.db"
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60        # 1 hour
    refresh_token_expire_days: int = 7
    max_login_attempts: int = 5
    lockout_minutes: int = 5

    class Config:
        env_file = ".env"


settings = Settings()
