from pydantic_settings import BaseSettings
from typing import Dict, Any

class Settings(BaseSettings):
    app_name: str = "Krishi Saarthi API"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000
    openai_api_key: str = ""
    
    # GPU Server Configuration
    gpu_server_base_url: str = "http://your-server:8000"
    gpu_health_endpoint: str = "/api/health/detailed"
    vllm_generate_endpoint: str = "/api/vllm/generate"
    gpu_timeout_seconds: int = 30

    # Twilio configs
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_PHONE_NUMBER: str = ""
    
    # YouTube Recommender configs
    GEMINI_API_KEY: str = ""
    YOUTUBE_API_KEY: str = ""
    FIREBASE_PROJECT_ID: str = ""
    FIREBASE_PRIVATE_KEY_ID: str = ""
    FIREBASE_PRIVATE_KEY: str = ""
    FIREBASE_CLIENT_EMAIL: str = ""
    FIREBASE_CLIENT_ID: str = ""
    FIREBASE_CLIENT_CERT_URL: str = ""
    FIREBASE_SERVICE_ACCOUNT_PATH: str = ""
    
    # Government Schemes RAG Configuration
    pinecone_api_key: str = ""
    GOOGLE_API_KEY: str = ""
    
    # YouTube search configuration
    YOUTUBE_MAX_RESULTS: int = 10  # Maximum videos to return (enforced)
    YOUTUBE_MIN_RESULTS: int = 3   # Minimum videos to return (enforced)
    YOUTUBE_SEARCH_LANGUAGES: str = "hi,en"  # Comma-separated languages
    YOUTUBE_VIDEO_DURATION: str = "medium"  # short, medium, long
    
    @property
    def firebase_config(self) -> Dict[str, Any]:
        """Generate Firebase configuration dictionary."""
        return {
            "type": "service_account",
            "project_id": self.FIREBASE_PROJECT_ID or "your_project_id",
            "private_key_id": self.FIREBASE_PRIVATE_KEY_ID or "your_private_key_id",
            "private_key": (self.FIREBASE_PRIVATE_KEY or "your_private_key").replace('\\n', '\n'),
            "client_email": self.FIREBASE_CLIENT_EMAIL or "your_client_email",
            "client_id": self.FIREBASE_CLIENT_ID or "your_client_id",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": self.FIREBASE_CLIENT_CERT_URL or "your_cert_url"
        }
    
    @property
    def youtube_config(self) -> Dict[str, Any]:
        """Generate YouTube search configuration dictionary."""
        return {
            'max_results': self.YOUTUBE_MAX_RESULTS,
            'min_results': self.YOUTUBE_MIN_RESULTS,
            'search_languages': self.YOUTUBE_SEARCH_LANGUAGES.split(','),
            'video_duration': self.YOUTUBE_VIDEO_DURATION
        }
    
    def validate_youtube_config(self) -> bool:
        """Validate YouTube recommender configuration."""
        required_fields = [
            self.GEMINI_API_KEY,
            self.YOUTUBE_API_KEY,
            self.FIREBASE_PROJECT_ID,
            self.FIREBASE_CLIENT_EMAIL
        ]
        return all(field.strip() for field in required_fields if field)

    class Config:
        env_file = ".env"

settings = Settings()