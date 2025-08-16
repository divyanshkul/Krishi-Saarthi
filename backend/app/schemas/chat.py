from pydantic import BaseModel
from typing import Optional
from enum import Enum


class WorkflowType(str, Enum):
    TEXT_ONLY = "text_only"
    TEXT_WITH_IMAGE = "text_with_image"
    AUDIO_ONLY = "audio_only"
    AUDIO_WITH_IMAGE = "audio_with_image"


class ResponseContent(BaseModel):
    text: str
    video_url: Optional[str] = None
    video_title: Optional[str] = None
    website_url: Optional[str] = None
    website_title: Optional[str] = None

    class Config:
        exclude_none = True

    def dict(self, **kwargs):
        kwargs['exclude_none'] = True
        return super().dict(**kwargs)


class ChatResponse(BaseModel):
    success: bool
    workflow_type: WorkflowType
    response: ResponseContent
    processed_files: Optional[list[str]] = None

    class Config:
        exclude_none = True

    def dict(self, **kwargs):
        kwargs['exclude_none'] = True
        return super().dict(**kwargs)


class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    detail: Optional[str] = None

    class Config:
        exclude_none = True