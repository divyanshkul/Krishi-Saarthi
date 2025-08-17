from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    app_name: str = "Krishi Saarthi API"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000
    openai_api_key: str = ""
    
    # Firebase Configuration
    firebase_project_id: Optional[str] = None
    firebase_service_account_path: Optional[str] = None
    firebase_client_email: Optional[str] = None
    firebase_private_key: Optional[str] = None
    firebase_private_key_id: Optional[str] = None
    firebase_client_id: Optional[str] = None
    
    class Config:
        env_file = ".env"

settings = Settings()