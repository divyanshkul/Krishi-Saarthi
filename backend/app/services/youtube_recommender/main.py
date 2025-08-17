"""
Simple Farming Video Recommender
Main application that orchestrates the complete flow:
1. Get crop data from Firebase
2. Detect farming stage
3. Generate keywords with LLM
4. Search YouTube videos
"""

from datetime import datetime
from typing import Dict, List

# Import from centralized config
try:
    from app.core.config import settings
    FIREBASE_CONFIG = settings.firebase_config
    GEMINI_API_KEY = settings.GEMINI_API_KEY
    YOUTUBE_API_KEY = settings.YOUTUBE_API_KEY
    YOUTUBE_CONFIG = settings.youtube_config
except ImportError:
    # Fallback for standalone usage
    from config import FIREBASE_CONFIG, GEMINI_API_KEY, YOUTUBE_API_KEY, YOUTUBE_CONFIG

from firebase_client import FirebaseClient
from stage_detector import CropStageDetector
from llm_generator import LLMKeywordGenerator
from youtube_client import YouTubeClient

class FarmingVideoRecommender:
    """Simple farming video recommendation system."""
    
    def __init__(self):
        """Initialize all components."""
        # Initialize clients
        self.firebase_client = FirebaseClient(FIREBASE_CONFIG)
        self.stage_detector = CropStageDetector(GEMINI_API_KEY)
        self.llm_generator = LLMKeywordGenerator(GEMINI_API_KEY)
        self.youtube_client = YouTubeClient(YOUTUBE_API_KEY)
    
    def get_recommendations(self, farmer_id: str, crop_id: str = None) -> Dict:
        try:
            # Step 1: Get crop data from Firebase
            if crop_id:
                crop_data = self.firebase_client.get_crop_details(farmer_id, crop_id)
                if not crop_data:
                    return {'success': False, 'error': f"Crop {crop_id} not found"}
            else:
                crops = self.firebase_client.get_farmer_crops(farmer_id)
                if not crops:
                    return {'success': False, 'error': f"No crops found for farmer {farmer_id}"}
                crop_data = crops[0]  # Use first crop
            
            # Step 2: Detect farming stage
            stage_data = self.stage_detector.detect_stage(crop_data)
            
            # Step 3: Generate search keywords
            keywords = self.llm_generator.generate_keywords(stage_data)
            
            # Step 4: Search YouTube videos
            videos = self.youtube_client.search_videos(keywords, YOUTUBE_CONFIG['max_results'])
            
            # Step 5: Return only titles and URLs
            video_list = []
            for video in videos:
                video_list.append({
                    'title': video['title'],
                    'url': video['url']
                })
            
            return {
                'success': True,
                'videos': video_list
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_farmer_overview(self, farmer_id: str) -> Dict:
        """Get overview of all crops for a farmer."""
        try:
            crops = self.firebase_client.get_farmer_crops(farmer_id)
            crop_summaries = []
            
            for crop in crops:
                stage_data = self.stage_detector.detect_stage(crop)
                crop_summaries.append({
                    'crop_id': crop.get('crop_id'),
                    'crop_type': crop.get('crop_type'),
                    'current_stage': stage_data['stage_name'],
                    'days_since_sowing': stage_data['days_since_sowing'],
                    'location': stage_data['location'],
                    'confidence': stage_data['confidence']
                })
            
            return {
                'success': True,
                'farmer_id': farmer_id,
                'total_crops': len(crops),
                'crops': crop_summaries
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_system_status(self) -> Dict:
        """Get status of all system components."""
        return {
            'firebase_connected': self.firebase_client.is_connected(),
            'llm_enabled': self.llm_generator.enabled,
            'youtube_enabled': self.youtube_client.enabled,
            'system_ready': all([
                self.firebase_client.is_connected(),  # Required
                self.llm_generator.enabled,  # Required
                self.youtube_client.enabled   # Required
            ])
        }

if __name__ == "__main__":
    # Simple test
    recommender = FarmingVideoRecommender()
    status = recommender.get_system_status()
    print("System Status:", status)
