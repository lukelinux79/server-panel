from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    app_name: str = "server-panel"
    api_prefix: str = "/api"
    debug: bool = True


settings = Settings()
