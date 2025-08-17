from fastapi import APIRouter, HTTPException, Depends, Header
from typing import Optional, List
from ..schemas.user_profile import UserProfileCreate, UserProfileUpdate, UserProfileResponse
from ..services.firebase_service import firebase_service

router = APIRouter(prefix="/user-profile", tags=["User Profile"])


@router.get("/health", response_model=dict)
async def check_firebase_health():
    """Check Firebase service status"""
    return {
        "firebase_available": firebase_service.is_available,
        "status": "operational" if firebase_service.is_available else "limited (no firebase)"
    }


async def verify_firebase_token(authorization: Optional[str] = Header(None)):
    """Verify Firebase ID token from Authorization header"""
    if not firebase_service.is_available:
        # For development without Firebase credentials, return a mock user
        return {"uid": "dev_user_123", "email": "dev@example.com"}
    
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header required")
    
    try:
        # Extract token from "Bearer <token>"
        token = authorization.split(" ")[1] if authorization.startswith("Bearer ") else authorization
        decoded_token = await firebase_service.verify_id_token(token)
        
        if not decoded_token:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        return decoded_token
    except IndexError:
        raise HTTPException(status_code=401, detail="Invalid authorization format")
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Token verification failed: {str(e)}")


@router.post("/", response_model=dict)
async def create_user_profile(
    profile: UserProfileCreate,
    user_token: dict = Depends(verify_firebase_token)
):
    """Create a new user profile"""
    try:
        user_id = user_token.get("uid")
        if not user_id:
            raise HTTPException(status_code=400, detail="Invalid user token")
        
        # Check if profile already exists
        existing_profile = await firebase_service.get_user_profile(user_id)
        if existing_profile:
            raise HTTPException(status_code=409, detail="User profile already exists")
        
        profile_data = profile.dict()
        success = await firebase_service.save_user_profile(user_id, profile_data)
        
        if success:
            return {"message": "Profile created successfully", "user_id": user_id}
        else:
            raise HTTPException(status_code=500, detail="Failed to create profile")
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/", response_model=UserProfileResponse)
async def get_user_profile(user_token: dict = Depends(verify_firebase_token)):
    """Get current user's profile"""
    try:
        user_id = user_token.get("uid")
        if not user_id:
            raise HTTPException(status_code=400, detail="Invalid user token")
        
        profile = await firebase_service.get_user_profile(user_id)
        
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        return UserProfileResponse(**profile)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.put("/", response_model=dict)
async def update_user_profile(
    profile_update: UserProfileUpdate,
    user_token: dict = Depends(verify_firebase_token)
):
    """Update current user's profile"""
    try:
        user_id = user_token.get("uid")
        if not user_id:
            raise HTTPException(status_code=400, detail="Invalid user token")
        
        # Check if profile exists
        existing_profile = await firebase_service.get_user_profile(user_id)
        if not existing_profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        # Only update fields that are provided
        update_data = {k: v for k, v in profile_update.dict().items() if v is not None}
        
        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        success = await firebase_service.update_user_profile(user_id, update_data)
        
        if success:
            return {"message": "Profile updated successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to update profile")
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.delete("/", response_model=dict)
async def delete_user_profile(user_token: dict = Depends(verify_firebase_token)):
    """Delete current user's profile"""
    try:
        user_id = user_token.get("uid")
        if not user_id:
            raise HTTPException(status_code=400, detail="Invalid user token")
        
        success = await firebase_service.delete_user_profile(user_id)
        
        if success:
            return {"message": "Profile deleted successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to delete profile")
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/all", response_model=List[UserProfileResponse])
async def get_all_user_profiles(limit: int = 100):
    """Get all user profiles (Admin endpoint - add authentication as needed)"""
    try:
        profiles = await firebase_service.get_all_user_profiles(limit)
        return [UserProfileResponse(**profile) for profile in profiles]
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
