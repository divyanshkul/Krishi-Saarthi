"""
Pydantic schemas for YouTube recommendation API endpoints.
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class VideoRecommendation(BaseModel):
    """Individual video recommendation model."""
    title: str
    url: str
    thumbnail: Optional[str] = None
    duration: Optional[str] = None
    channel: Optional[str] = None


class CropStageInfo(BaseModel):
    """Crop stage information model."""
    crop_id: Optional[str] = None
    crop_type: str
    variety: Optional[str] = None
    current_stage: str
    days_since_sowing: int
    location: str
    confidence: float = Field(ge=0.0, le=1.0)
    sowing_date: Optional[str] = None


class VideoRecommendationRequest(BaseModel):
    """Request model for video recommendations."""
    farmer_id: str = Field(..., description="Unique identifier for the farmer")
    crop_id: Optional[str] = Field(None, description="Optional specific crop ID")


class VideoRecommendationResponse(BaseModel):
    """Response model for video recommendations."""
    success: bool
    farmer_id: str
    crop_id: Optional[str] = None
    crop_type: Optional[str] = None
    current_stage: Optional[str] = None
    videos: List[VideoRecommendation]
    total_videos: int
    error: Optional[str] = None

    class Config:
        exclude_none = True


class FarmerOverviewRequest(BaseModel):
    """Request model for farmer overview."""
    farmer_id: str = Field(..., description="Unique identifier for the farmer")


class FarmerOverviewResponse(BaseModel):
    """Response model for farmer overview."""
    success: bool
    farmer_id: str
    total_crops: int
    crops: List[CropStageInfo]
    last_updated: str
    error: Optional[str] = None

    class Config:
        exclude_none = True


class SystemStatusResponse(BaseModel):
    """Response model for system status."""
    firebase_connected: bool
    llm_enabled: bool
    youtube_enabled: bool
    system_ready: bool
    timestamp: str
    error: Optional[str] = None

    class Config:
        exclude_none = True


class KeywordSearchRequest(BaseModel):
    """Request model for keyword-based video search."""
    keywords: List[str] = Field(..., description="List of search keywords")
    max_results: int = Field(default=10, ge=1, le=50, description="Maximum number of videos to return")


class KeywordSearchResponse(BaseModel):
    """Response model for keyword-based video search."""
    success: bool
    keywords: List[str]
    videos: List[VideoRecommendation]
    total_videos: int
    error: Optional[str] = None

    class Config:
        exclude_none = True


class YouTubeErrorResponse(BaseModel):
    """Error response model for YouTube recommendation API."""
    success: bool = False
    error: str
    detail: Optional[str] = None
    farmer_id: Optional[str] = None
    timestamp: Optional[str] = None

    class Config:
        exclude_none = True
