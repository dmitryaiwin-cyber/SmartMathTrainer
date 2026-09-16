import os
from typing import Literal
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite:///./math_project.db"
    secret_key: str = "dev-secret-key-change-in-production"
    debug: bool = False
    
    model_config = {"env_file": ".env", "case_sensitive": False}


settings = Settings()
