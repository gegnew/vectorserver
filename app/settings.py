from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env")

    app_title: str = "Vector Database API"
    app_version: str = "0.1.0"
    app_description: str = "REST API for vector database"

    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 8000

    cohere_api_key: str | None = None
    db_path: str = "data/demo.sqlite"


settings = Settings()
