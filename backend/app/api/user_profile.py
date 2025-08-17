

from fastapi import APIRouter, HTTPException, Query
from ..schemas.user_profile import UserProfileResponse
from ..services.firebase_service import firebase_service


router = APIRouter(prefix="/user-profile", tags=["User Profile"])





# Fetch user profile from Firebase by user_id (query param)
@router.get("/", response_model=UserProfileResponse)
async def get_user_profile(user_id: str = Query(..., description="User ID to fetch profile for")):
    """Fetch user profile from Firebase by user_id"""
    profile = await firebase_service.get_user_profile(user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return UserProfileResponse(**profile)
