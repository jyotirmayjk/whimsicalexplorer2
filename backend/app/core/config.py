from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "Kids Pokédex"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        # Fallback to SQLite for immediate local testing without Postgres
        return "sqlite:///./kids_pokedex.db"

    # Auth
    SECRET_KEY: str = "DEVELOPMENT_MODE_SUPER_SECRET_KEY_CHANGE_ME"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # ADK / Gemini
    GOOGLE_API_KEY: str = ""

    model_config = {
        "case_sensitive": True,
        "env_file": ".env",
        "env_file_encoding": "utf-8",
    }


settings = Settings()
