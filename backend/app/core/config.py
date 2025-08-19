import os


class Settings:
    PROJECT_NAME: str = "FastAPI Onion Architecture"
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", "postgresql+psycopg2://postgres:postgres@localhost:5432/app_db"
    )
    API_V1_STR: str = "/api/v1"
    DB_USER: str = os.getenv("DB_USER", "postgres")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "postgres")
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: str = os.getenv("DB_PORT", "5432")
    DB_NAME: str = os.getenv("DB_NAME", "app_db")
    SQLALCHEMY_DATABASE_URI: str = (
        f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

    # AI/LLM & Media (optional)
    OPENAI_API_KEY: str | None = os.getenv("OPENAI_API_KEY")
    OPENAI_CHAT_MODEL: str = os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini")
    OPENAI_EMBED_MODEL: str = os.getenv("OPENAI_EMBED_MODEL", "text-embedding-3-small")
    WHISPER_MODEL: str = os.getenv("WHISPER_MODEL", "base")

    # Payments (Stripe)
    STRIPE_SECRET_KEY: str | None = os.getenv("STRIPE_SECRET_KEY")
    STRIPE_WEBHOOK_SECRET: str | None = os.getenv("STRIPE_WEBHOOK_SECRET")
    STRIPE_DEFAULT_CURRENCY: str = os.getenv("STRIPE_DEFAULT_CURRENCY", "usd")

    class Config:
        env_file = os.getenv("ENV_FILE", ".env")  # Mặc định dùng .env


settings = Settings()
