"""
Firebase client for retrieving crop data.
Simple interface to get farmer and crop information.
"""

import firebase_admin
from firebase_admin import credentials, firestore
from typing import Dict, List, Optional

class FirebaseClient:
    """Simple Firebase client for crop data retrieval."""
    
    def __init__(self, config: Dict):
        """Initialize Firebase client with configuration."""
        try:
            if not firebase_admin._apps:
                # Try service account path first, then direct config
                try:
                    from app.core.config import settings
                    firebase_service_account_path = settings.FIREBASE_SERVICE_ACCOUNT_PATH
                except ImportError:
                    # Fallback for standalone usage
                    import os
                    firebase_service_account_path = os.getenv('FIREBASE_SERVICE_ACCOUNT_PATH')
                
                if firebase_service_account_path and firebase_service_account_path != 'None':
                    # Use service account JSON file
                    cred = credentials.Certificate(firebase_service_account_path)
                else:
                    # Use direct configuration
                    cred = credentials.Certificate(config)
                
                firebase_admin.initialize_app(cred)
            
            self.db = firestore.client()
        except Exception as e:
            raise ValueError(f"Failed to initialize Firebase: {e}")
    
    def get_farmer_crops(self, farmer_id: str) -> List[Dict]:
        """
        Get all crops for a farmer.
        
        Args:
            farmer_id: Unique farmer identifier
            
        Returns:
            List of crop dictionaries with: crop_type, sowing_date, district, state
        """
        if not self.db:
            raise ValueError("Firebase not connected")
        
        try:
            crops_ref = self.db.collection('farmers').document(farmer_id).collection('crops')
            crops = crops_ref.stream()
            
            crop_list = []
            for crop in crops:
                crop_data = crop.to_dict()
                crop_data['crop_id'] = crop.id
                crop_list.append(crop_data)
            
            return crop_list
            
        except Exception as e:
            raise ValueError(f"Error retrieving crops for farmer {farmer_id}: {e}")
    
    def get_crop_details(self, farmer_id: str, crop_id: str) -> Optional[Dict]:
        """
        Get specific crop details.
        
        Args:
            farmer_id: Farmer identifier
            crop_id: Crop identifier
            
        Returns:
            Crop dictionary or None if not found
        """
        if not self.db:
            raise ValueError("Firebase not connected")
        
        try:
            crop_ref = self.db.collection('farmers').document(farmer_id).collection('crops').document(crop_id)
            crop = crop_ref.get()
            
            if crop.exists:
                crop_data = crop.to_dict()
                crop_data['crop_id'] = crop.id
                return crop_data
            else:
                return None
                
        except Exception as e:
            raise ValueError(f"Error retrieving crop {crop_id} for farmer {farmer_id}: {e}")
    
    def is_connected(self) -> bool:
        """Check if Firebase connection is active."""
        return self.db is not None
