from fastapi import FastAPI
import uvicorn
from app.api.router import api_router
from app.core.config import settings
from app.utils.logger import setup_logging

setup_logging()

app = FastAPI(
    title=settings.app_name,
    description="Backend API for Krishi Saarthi agricultural services",
    version="0.1.0",
)

@app.get("/")
async def health_check():
    return {"status": "healthy"}

app.include_router(api_router, prefix="/api")

if __name__ == "__main__":
    log_level = "debug" if settings.debug else "info"
    uvicorn.run(
        "main:app", 
        host=settings.host, 
        port=settings.port, 
        reload=settings.debug,
        log_level=log_level
    )