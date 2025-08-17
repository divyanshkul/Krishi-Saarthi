"""
Configuration file for the farming video recommender.
Uses centralized configuration from app.core.config.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import centralized settings
try:
    from app.core.config import settings
    
    # API Keys from centralized config
    GEMINI_API_KEY = settings.GEMINI_API_KEY
    YOUTUBE_API_KEY = settings.YOUTUBE_API_KEY
    
    # Firebase configuration from centralized config
    FIREBASE_CONFIG = settings.firebase_config
    FIREBASE_SERVICE_ACCOUNT_PATH = settings.FIREBASE_SERVICE_ACCOUNT_PATH
    
    # YouTube search settings from centralized config
    YOUTUBE_CONFIG = settings.youtube_config
    
    # Validate configuration
    if not settings.validate_youtube_config():
        # Fallback to environment variables if centralized config is incomplete
        GEMINI_API_KEY = GEMINI_API_KEY or os.getenv('GEMINI_API_KEY')
        YOUTUBE_API_KEY = YOUTUBE_API_KEY or os.getenv('YOUTUBE_API_KEY')
        
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not found in settings or environment variables")
        if not YOUTUBE_API_KEY:
            raise ValueError("YOUTUBE_API_KEY not found in settings or environment variables")
    
except ImportError:
    # Complete fallback to environment variables if centralized config is not available
    print("Warning: Could not import centralized settings, using environment variables only")
    
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
    
    FIREBASE_CONFIG = {
        "type": "service_account",
        "project_id": os.getenv('FIREBASE_PROJECT_ID', 'your_project_id'),
        "private_key_id": os.getenv('FIREBASE_PRIVATE_KEY_ID', 'your_private_key_id'),
        "private_key": os.getenv('FIREBASE_PRIVATE_KEY', 'your_private_key').replace('\\n', '\n'),
        "client_email": os.getenv('FIREBASE_CLIENT_EMAIL', 'your_client_email'),
        "client_id": os.getenv('FIREBASE_CLIENT_ID', 'your_client_id'),
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token", 
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": os.getenv('FIREBASE_CLIENT_CERT_URL', 'your_cert_url')
    }
    
    FIREBASE_SERVICE_ACCOUNT_PATH = os.getenv('FIREBASE_SERVICE_ACCOUNT_PATH')
    
    YOUTUBE_CONFIG = {
        'max_results': int(os.getenv('YOUTUBE_MAX_RESULTS', '15')),
        'search_languages': os.getenv('YOUTUBE_SEARCH_LANGUAGES', 'hi,en').split(','),
        'video_duration': os.getenv('YOUTUBE_VIDEO_DURATION', 'medium')
    }
    
    # Validate required API keys
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY environment variable is required")
    if not YOUTUBE_API_KEY:
        raise ValueError("YOUTUBE_API_KEY environment variable is required")
