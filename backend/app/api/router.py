from fastapi import APIRouter
from app.api import health, chat, twilio, youtube_recommendation, guided_mode
from app.api.schemes import router as schemes_router

api_router = APIRouter()

api_router.include_router(health.router)
api_router.include_router(chat.router)
api_router.include_router(twilio.router)
api_router.include_router(youtube_recommendation.router)
api_router.include_router(guided_mode.router)
api_router.include_router(schemes_router.router)
