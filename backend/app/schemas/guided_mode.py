"""
Pydantic schemas for the guided mode API.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum

class StageType(str, Enum):
    """Farming stage types"""
    SOIL_PREPARATION = "soil_preparation"
    SEED_SOWING = "seed_sowing"
    CROP_GROWTH = "crop_growth"
    HARVESTING = "harvesting"
    POST_HARVEST = "post_harvest"

class GuidanceTopic(BaseModel):
    """Individual guidance topic within a stage"""
    title: str = Field(..., description="Title of the guidance topic")
    icon: str = Field(..., description="Icon identifier for the topic")
    description: str = Field(..., description="Detailed guidance description")
    video_links: List[str] = Field(default=[], description="YouTube video links for complex techniques")
    articles: List[str] = Field(default=[], description="Article links for additional reading")

class StageGuidance(BaseModel):
    """Guidance for a specific farming stage"""
    stage_name: str = Field(..., description="Human-readable stage name")
    stage_type: StageType = Field(..., description="Stage type identifier")
    topics: List[GuidanceTopic] = Field(..., description="List of guidance topics for this stage")

class GuidedModeResponse(BaseModel):
    """Complete response for guided mode API"""
    success: bool = Field(..., description="Whether the request was successful")
    crop_name: str = Field(..., description="Name of the crop")
    stages: Dict[str, StageGuidance] = Field(..., description="Guidance for all farming stages")
    timestamp: str = Field(..., description="Response timestamp")
    error: Optional[str] = Field(None, description="Error message if any")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "crop_name": "wheat",
                "stages": {
                    "soilPrep": {
                        "stage_name": "Soil Preparation",
                        "stage_type": "soil_preparation",
                        "topics": [
                            {
                                "title": "Plowing Depth and Technique",
                                "icon": "plow",
                                "description": "For wheat cultivation in Indian soil conditions, deep plowing (15-20 cm) is recommended...",
                                "video_links": ["https://youtube.com/watch?v=example"],
                                "articles": []
                            }
                        ]
                    }
                },
                "timestamp": "2025-08-18T10:30:00Z"
            }
        }

class GuidedModeErrorResponse(BaseModel):
    """Error response for guided mode API"""
    success: bool = Field(False, description="Request success status")
    error: str = Field(..., description="Error message")
    timestamp: str = Field(..., description="Error timestamp")
