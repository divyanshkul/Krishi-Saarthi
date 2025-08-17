from pydantic_settings import BaseSettings

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
    
    class Config:
        env_file = ".env"

settings = Settings()