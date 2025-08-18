"""
YouTube Video Recommendation Service
Integrates the YouTube Recommender into the main backend structure.
"""

import os
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

from app.utils.logger import get_logger
from app.core.config import settings

# Import YouTube Recommender components from local services directory
try:
    from app.services.youtube_recommender.firebase_client import FirebaseClient
    from app.services.youtube_recommender.stage_detector import CropStageDetector
    from app.services.youtube_recommender.llm_generator import LLMKeywordGenerator
    from app.services.youtube_recommender.youtube_client import YouTubeClient
except ImportError as e:
    raise ImportError(f"Failed to import YouTube Recommender components: {e}")

logger = get_logger(__name__)


class YouTubeRecommendationService:
    """Service for getting farming video recommendations using YouTube API."""
    
    def __init__(self):
        """Initialize the YouTube recommendation service."""
        self._recommender = None
        self._initialize_recommender()
    
    def _initialize_recommender(self):
        """Initialize the FarmingVideoRecommender with error handling."""
        try:
            # Initialize clients using centralized settings
            self.firebase_client = FirebaseClient(settings.firebase_config)
            self.stage_detector = CropStageDetector(settings.GEMINI_API_KEY)
            self.llm_generator = LLMKeywordGenerator(settings.GEMINI_API_KEY)
            self.youtube_client = YouTubeClient(settings.YOUTUBE_API_KEY)
            
            logger.info("YouTube recommendation service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize YouTube recommendation service: {e}")
            raise
    
    async def get_video_recommendations(
        self, 
        farmer_id: str, 
        crop_id: Optional[str] = None,
        min_videos: int = 3,
        max_videos: int = 10
    ) -> Dict:
        """
        Get video recommendations for a farmer's crops.
        Ensures minimum 3 videos and maximum 10 videos are returned.
        
        Args:
            farmer_id: Unique identifier for the farmer
            crop_id: Optional specific crop ID, if not provided uses first crop
            min_videos: Minimum number of videos to return (default 3)
            max_videos: Maximum number of videos to return (default 10)
            
        Returns:
            Dict containing success status and video recommendations
        """
        try:
            logger.info(f"Getting video recommendations for farmer: {farmer_id}")
            
            # Enforce video count limits
            min_videos = max(min_videos, 3)  # Minimum 3 videos
            max_videos = min(max_videos, 10)  # Maximum 10 videos
            
            # Step 1: Get crop data from Firebase
            if crop_id:
                crop_data = self.firebase_client.get_crop_details(farmer_id, crop_id)
                if not crop_data:
                    logger.warning(f"Crop {crop_id} not found for farmer {farmer_id}")
                    return {
                        'success': False, 
                        'error': f"Crop {crop_id} not found",
                        'farmer_id': farmer_id,
                        'crop_id': crop_id
                    }
            else:
                crops = self.firebase_client.get_farmer_crops(farmer_id)
                if not crops:
                    logger.warning(f"No crops found for farmer {farmer_id}")
                    return {
                        'success': False, 
                        'error': f"No crops found for farmer {farmer_id}",
                        'farmer_id': farmer_id
                    }
                crop_data = crops[0]  # Use first crop
            
            # Step 2: Detect farming stage
            stage_data = self.stage_detector.detect_stage(crop_data)
            logger.info(f"Detected stage: {stage_data.get('stage_name')} for crop: {crop_data.get('crop_type')}")
            
            # Step 3: Generate search keywords
            keywords = self.llm_generator.generate_keywords(stage_data)
            logger.info(f"Generated keywords: {keywords}")
            
            # Step 4: Search YouTube videos with min/max constraints
            videos = self.youtube_client.search_videos(keywords, max_videos, min_videos)
            
            # Step 5: Validate video count and ensure minimum
            if len(videos) < min_videos:
                logger.warning(f"Only found {len(videos)} videos, less than minimum {min_videos}")
                # Try to get more videos with broader search
                videos = self._ensure_minimum_video_count(videos, keywords, min_videos, max_videos)
            
            # Step 6: Format response
            video_list = []
            for video in videos[:max_videos]:  # Ensure we don't exceed maximum
                video_list.append({
                    'title': video['title'],
                    'url': video['url'],
                    'thumbnail': video.get('thumbnail', ''),
                    'duration': video.get('duration', ''),
                    'channel': video.get('channel', '')
                })
            
            logger.info(f"Returning {len(video_list)} video recommendations)")
            
            return {
                'success': True,
                'farmer_id': farmer_id,
                'crop_id': crop_data.get('crop_id'),
                'crop_type': crop_data.get('crop_type'),
                'current_stage': stage_data.get('stage_name'),
                'videos': video_list,
                'total_videos': len(video_list),
                'min_videos_requested': min_videos,
                'max_videos_requested': max_videos
            }
            
        except Exception as e:
            logger.error(f"Error getting video recommendations: {e}")
            return {
                'success': False, 
                'error': str(e),
                'farmer_id': farmer_id
            }
    
    def _ensure_minimum_video_count(self, current_videos: List, keywords: Dict, min_videos: int, max_videos: int) -> List:
        """
        Ensure we have at least the minimum number of videos by trying additional searches.
        
        Args:
            current_videos: List of videos already found
            keywords: Original search keywords
            min_videos: Minimum number of videos required
            max_videos: Maximum number of videos allowed
            
        Returns:
            List of videos with at least min_videos count
        """
        if len(current_videos) >= min_videos:
            return current_videos
        
        try:
            logger.info(f"Attempting to find more videos. Current: {len(current_videos)}, needed: {min_videos}")
            
            # Create broader search terms
            fallback_keywords = {
                'primary_keywords': ['farming', 'agriculture', 'कृषि', 'खेती'],
                'secondary_keywords': ['farming tips', 'agriculture techniques', 'crop management'],
                'search_terms': ['modern farming', 'sustainable agriculture', 'farming basics']
            }
            
            # Try to get additional videos
            additional_videos = self.youtube_client.search_videos(
                fallback_keywords, 
                max_videos - len(current_videos),
                min_videos - len(current_videos)
            )
            
            # Combine and deduplicate
            all_videos = current_videos + additional_videos
            unique_videos = []
            seen_urls = set()
            
            for video in all_videos:
                if video.get('url') not in seen_urls:
                    seen_urls.add(video.get('url'))
                    unique_videos.append(video)
                    
                if len(unique_videos) >= max_videos:
                    break
            
            logger.info(f"After fallback search: {len(unique_videos)} total videos")
            return unique_videos
            
        except Exception as e:
            logger.error(f"Error in fallback video search: {e}")
            return current_videos
    
    async def get_farmer_overview(self, farmer_id: str) -> Dict:
        """
        Get overview of all crops for a farmer.
        
        Args:
            farmer_id: Unique identifier for the farmer
            
        Returns:
            Dict containing farmer overview with all crops and their stages
        """
        try:
            logger.info(f"Getting farmer overview for: {farmer_id}")
            
            crops = self.firebase_client.get_farmer_crops(farmer_id)
            if not crops:
                return {
                    'success': False,
                    'error': f"No crops found for farmer {farmer_id}",
                    'farmer_id': farmer_id
                }
            
            crop_summaries = []
            
            for crop in crops:
                try:
                    stage_data = self.stage_detector.detect_stage(crop)
                    crop_summaries.append({
                        'crop_id': crop.get('crop_id'),
                        'crop_type': crop.get('crop_type'),
                        'variety': crop.get('variety'),
                        'current_stage': stage_data['stage_name'],
                        'days_since_sowing': stage_data['days_since_sowing'],
                        'location': stage_data['location'],
                        'confidence': stage_data['confidence'],
                        'sowing_date': crop.get('sowing_date')
                    })
                except Exception as crop_error:
                    logger.warning(f"Error processing crop {crop.get('crop_id')}: {crop_error}")
                    continue
            
            logger.info(f"Generated overview for {len(crop_summaries)} crops")
            
            return {
                'success': True,
                'farmer_id': farmer_id,
                'total_crops': len(crop_summaries),
                'crops': crop_summaries,
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting farmer overview: {e}")
            return {
                'success': False, 
                'error': str(e),
                'farmer_id': farmer_id
            }
    
    async def get_system_status(self) -> Dict:
        """
        Get status of all YouTube recommendation system components.
        
        Returns:
            Dict containing system status information
        """
        try:
            status = {
                'firebase_connected': self.firebase_client.is_connected(),
                'llm_enabled': self.llm_generator.enabled,
                'youtube_enabled': self.youtube_client.enabled,
                'system_ready': False,
                'timestamp': datetime.now().isoformat()
            }
            
            # System is ready if all required components are available
            status['system_ready'] = all([
                status['firebase_connected'],
                status['llm_enabled'],
                status['youtube_enabled']
            ])
            
            logger.info(f"System status check completed: ready={status['system_ready']}")
            return status
            
        except Exception as e:
            logger.error(f"Error checking system status: {e}")
            return {
                'firebase_connected': False,
                'llm_enabled': False,
                'youtube_enabled': False,
                'system_ready': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def search_videos_by_keywords(
        self, 
        keywords: List[str], 
        max_results: int = 10,
        min_results: int = 3
    ) -> Dict:
        """
        Search videos directly by keywords without farmer/crop context.
        Ensures minimum 3 videos and maximum 10 videos are returned.
        
        Args:
            keywords: List of search keywords
            max_results: Maximum number of videos to return (capped at 10)
            min_results: Minimum number of videos to return (default 3)
            
        Returns:
            Dict containing search results
        """
        try:
            logger.info(f"Searching videos for keywords: {keywords}")
            
            # Enforce limits
            max_results = min(max_results, 10)
            min_results = max(min_results, 3)
            
            # Convert keywords list to the format expected by youtube_client
            keyword_dict = {
                'primary_keywords': keywords[:5],
                'secondary_keywords': keywords[5:10] if len(keywords) > 5 else [],
                'search_terms': keywords
            }
            
            # Search with min/max constraints
            videos = self.youtube_client.search_videos(keyword_dict, max_results, min_results)
            
            # Format video list
            video_list = []
            for video in videos:
                video_list.append({
                    'title': video['title'],
                    'url': video['url'],
                    'thumbnail': video.get('thumbnail', ''),
                    'duration': video.get('duration', ''),
                    'channel': video.get('channel', '')
                })
            
            logger.info(f"Found {len(video_list)} videos for keywords (min: {min_results}, max: {max_results})")
            
            return {
                'success': True,
                'keywords': keywords,
                'videos': video_list,
                'total_videos': len(video_list),
                'min_videos_requested': min_results,
                'max_videos_requested': max_results
            }
            
        except Exception as e:
            logger.error(f"Error searching videos by keywords: {e}")
            return {
                'success': False,
                'error': str(e),
                'keywords': keywords
            }
