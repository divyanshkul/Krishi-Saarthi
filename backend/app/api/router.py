from fastapi import APIRouter
from app.api import health, chat, user_profile

api_router = APIRouter()

api_router.include_router(health.router)
api_router.include_router(chat.router)
api_router.include_router(user_profile.router)
