from pydantic import BaseSettings

class Settings(BaseSettings):
    app_name: str = "server-panel"
    api_prefix: str = "/api"
    debug: bool = True

    class Config:
        env_file = ".env"

settings = Settings()
