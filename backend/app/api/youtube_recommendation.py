"""
API routes for YouTube video recommendations.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional

from app.schemas.youtube_recommendation import (
    VideoRecommendationRequest,
    VideoRecommendationResponse,
    FarmerOverviewRequest,
    FarmerOverviewResponse,
    SystemStatusResponse,
    KeywordSearchRequest,
    KeywordSearchResponse,
    YouTubeErrorResponse
)
from app.services.youtube_recommendation_service import YouTubeRecommendationService
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/youtube", tags=["YouTube Recommendations"])

# Dependency to get the YouTube recommendation service
def get_youtube_service() -> YouTubeRecommendationService:
    """Dependency to get YouTube recommendation service instance."""
    return YouTubeRecommendationService()


@router.get(
    "/farmer/{farmer_id}/videos",
    response_model=VideoRecommendationResponse,
    summary="Get video recommendations for a farmer",
    description="Get personalized farming video recommendations based on farmer's crop data and current farming stage. Always returns between 3-10 videos."
)
async def get_farmer_video_recommendations(
    farmer_id: str,
    crop_id: Optional[str] = Query(None, description="Optional specific crop ID"),
    min_videos: int = Query(3, ge=3, le=10, description="Minimum number of videos (3-10)"),
    max_videos: int = Query(10, ge=3, le=10, description="Maximum number of videos (3-10)"),
    youtube_service: YouTubeRecommendationService = Depends(get_youtube_service)
):
    """Get video recommendations for a specific farmer with guaranteed video count."""
    try:
        logger.info(f"API request for video recommendations: farmer_id={farmer_id}, crop_id={crop_id}, min={min_videos}, max={max_videos}")
        
        # Validate min/max relationship
        if min_videos > max_videos:
            raise HTTPException(
                status_code=400,
                detail="min_videos cannot be greater than max_videos"
            )
        
        result = await youtube_service.get_video_recommendations(
            farmer_id, crop_id, min_videos, max_videos
        )
        
        if not result['success']:
            raise HTTPException(
                status_code=404 if "not found" in result.get('error', '').lower() else 400,
                detail=result.get('error', 'Failed to get video recommendations')
            )
        
        return VideoRecommendationResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_farmer_video_recommendations: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get(
    "/farmer/{farmer_id}/overview",
    response_model=FarmerOverviewResponse,
    summary="Get farmer crop overview",
    description="Get comprehensive overview of all crops for a farmer including current stages and recommendations."
)
async def get_farmer_overview(
    farmer_id: str,
    youtube_service: YouTubeRecommendationService = Depends(get_youtube_service)
):
    """Get overview of all crops for a farmer."""
    try:
        logger.info(f"API request for farmer overview: farmer_id={farmer_id}")
        
        result = await youtube_service.get_farmer_overview(farmer_id)
        
        if not result['success']:
            raise HTTPException(
                status_code=404 if "not found" in result.get('error', '').lower() else 400,
                detail=result.get('error', 'Failed to get farmer overview')
            )
        
        return FarmerOverviewResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_farmer_overview: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get(
    "/system/status",
    response_model=SystemStatusResponse,
    summary="Check system status",
    description="Check the status of all YouTube recommendation system components (Firebase, LLM, YouTube API)."
)
async def get_system_status(
    youtube_service: YouTubeRecommendationService = Depends(get_youtube_service)
):
    """Get system status for YouTube recommendation service."""
    try:
        logger.info("API request for system status")
        
        result = await youtube_service.get_system_status()
        return SystemStatusResponse(**result)
        
    except Exception as e:
        logger.error(f"Unexpected error in get_system_status: {e}")
        # Return a basic status response even if there's an error
        return SystemStatusResponse(
            firebase_connected=False,
            llm_enabled=False,
            youtube_enabled=False,
            system_ready=False,
            timestamp="",
            error=str(e)
        )


@router.post(
    "/search/keywords",
    response_model=KeywordSearchResponse,
    summary="Search videos by keywords",
    description="Search for farming videos using custom keywords without farmer/crop context. Always returns between 3-10 videos."
)
async def search_videos_by_keywords(
    request: KeywordSearchRequest,
    youtube_service: YouTubeRecommendationService = Depends(get_youtube_service)
):
    """Search videos directly by keywords with guaranteed video count."""
    try:
        logger.info(f"API request for keyword search: keywords={request.keywords}, max={request.max_results}")
        
        # Enforce min_results if not in request (for backward compatibility)
        min_results = getattr(request, 'min_results', 3)
        
        result = await youtube_service.search_videos_by_keywords(
            request.keywords, 
            request.max_results,
            min_results
        )
        
        if not result['success']:
            raise HTTPException(
                status_code=400,
                detail=result.get('error', 'Failed to search videos')
            )
        
        return KeywordSearchResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in search_videos_by_keywords: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get(
    "/search",
    response_model=KeywordSearchResponse,
    summary="Search videos by keywords (GET method)",
    description="Search for farming videos using keywords via GET request. Always returns between 3-10 videos."
)
async def search_videos_by_keywords_get(
    keywords: List[str] = Query(..., description="Search keywords"),
    max_results: int = Query(default=10, ge=3, le=10, description="Maximum number of videos (3-10)"),
    min_results: int = Query(default=3, ge=3, le=10, description="Minimum number of videos (3-10)"),
    youtube_service: YouTubeRecommendationService = Depends(get_youtube_service)
):
    """Search videos by keywords using GET method with guaranteed video count."""
    try:
        logger.info(f"API GET request for keyword search: keywords={keywords}, min={min_results}, max={max_results}")
        
        # Validate min/max relationship
        if min_results > max_results:
            raise HTTPException(
                status_code=400,
                detail="min_results cannot be greater than max_results"
            )
        
        result = await youtube_service.search_videos_by_keywords(keywords, max_results, min_results)
        
        if not result['success']:
            raise HTTPException(
                status_code=400,
                detail=result.get('error', 'Failed to search videos')
            )
        
        return KeywordSearchResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in search_videos_by_keywords_get: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# Health check endpoint for the YouTube service
@router.get(
    "/health",
    summary="YouTube service health check",
    description="Simple health check for the YouTube recommendation service."
)
async def youtube_service_health():
    """Health check endpoint for YouTube recommendation service."""
    try:
        youtube_service = YouTubeRecommendationService()
        status = await youtube_service.get_system_status()
        
        return {
            "status": "healthy" if status.get('system_ready', False) else "degraded",
            "service": "youtube_recommendation",
            "timestamp": status.get('timestamp'),
            "components": {
                "firebase": status.get('firebase_connected', False),
                "llm": status.get('llm_enabled', False),
                "youtube": status.get('youtube_enabled', False)
            }
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "service": "youtube_recommendation",
            "error": str(e)
        }
