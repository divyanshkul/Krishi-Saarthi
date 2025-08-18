"""
API routes for AI-powered agricultural guidance system.
"""

from fastapi import APIRouter, HTTPException, Depends, Path, Query
from typing import Optional

from app.schemas.guided_mode import GuidedModeResponse, GuidedModeErrorResponse
from app.services.guided_mode_service import GuidedModeService
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/guided-mode", tags=["Agricultural Guidance"])

# Dependency to get the guided mode service
def get_guided_mode_service() -> GuidedModeService:
    """Dependency to get guided mode service instance."""
    return GuidedModeService()

@router.get(
    "/{crop_name}",
    response_model=GuidedModeResponse,
    summary="Get AI-powered agricultural guidance for a crop",
    description="Get comprehensive farming guidance for all 5 stages of cultivation for a specific crop, powered by Gemini AI with Indian agricultural context."
)
async def get_crop_guidance(
    crop_name: str = Path(..., description="Name of the crop (e.g., wheat, rice, maize)", min_length=2),
    farmer_id: Optional[str] = Query(None, description="Optional farmer ID for personalized guidance"),
    guided_service: GuidedModeService = Depends(get_guided_mode_service)
):
    """Get comprehensive agricultural guidance for a specific crop."""
    try:
        logger.info(f"API request for crop guidance: crop_name={crop_name}, farmer_id={farmer_id}")
        
        # Validate crop name
        if not crop_name or len(crop_name.strip()) < 2:
            raise HTTPException(
                status_code=400,
                detail="Invalid crop name. Please provide a valid crop name."
            )
        
        # Clean crop name
        clean_crop_name = crop_name.strip().lower()
        
        result = await guided_service.get_crop_guidance(clean_crop_name, farmer_id)
        
        if not result['success']:
            raise HTTPException(
                status_code=500,
                detail=result.get('error', 'Failed to generate crop guidance')
            )
        
        return GuidedModeResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_crop_guidance: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Health check endpoint for the guided mode service  
@router.get(
    "/health",
    summary="Guided mode service health check",
    description="Simple health check for the agricultural guidance service."
)
async def guided_mode_health():
    """Health check endpoint for guided mode service."""
    try:
        guided_service = GuidedModeService()
        health_status = guided_service.is_healthy()
        
        return {
            "status": "healthy" if health_status['service_ready'] else "degraded",
            "service": "guided_mode",
            "timestamp": "2025-08-18T10:30:00Z",
            "components": health_status
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy", 
            "service": "guided_mode",
            "error": str(e),
            "timestamp": "2025-08-18T10:30:00Z"
        }
