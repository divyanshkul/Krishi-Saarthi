import firebase_admin
from firebase_admin import credentials, firestore, auth
from typing import Optional, Dict, Any, List
import os
from datetime import datetime
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class FirebaseService:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FirebaseService, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self._db = None
            self._firebase_available = self._initialize_firebase()
            self._initialized = True

    def _initialize_firebase(self) -> bool:
        """Initialize Firebase Admin SDK"""
        if firebase_admin._apps:
            self._db = firestore.client()
            return True
            
        try:
            # Method 1: Try service account key file
            cred_path = os.getenv('FIREBASE_SERVICE_ACCOUNT_PATH')
            if cred_path and os.path.exists(cred_path):
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred)
                self._db = firestore.client()
                print("Firebase initialized with service account key file")
                return True
            
            # Method 2: Try service account from environment variables
            project_id = os.getenv('FIREBASE_PROJECT_ID')
            client_email = os.getenv('FIREBASE_CLIENT_EMAIL')
            private_key = os.getenv('FIREBASE_PRIVATE_KEY')
            
            if project_id and client_email and private_key:
                # Create credentials from environment variables
                service_account_info = {
                    "type": "service_account",
                    "project_id": project_id,
                    "client_email": client_email,
                    "private_key": private_key.replace('\\n', '\n'),
                    "private_key_id": os.getenv('FIREBASE_PRIVATE_KEY_ID', ''),
                    "client_id": os.getenv('FIREBASE_CLIENT_ID', ''),
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                }
                
                cred = credentials.Certificate(service_account_info)
                firebase_admin.initialize_app(cred)
                self._db = firestore.client()
                print("Firebase initialized with environment variables")
                return True
            
            # Method 3: Try default credentials (works in production)
            firebase_admin.initialize_app()
            self._db = firestore.client()
            print("Firebase initialized with default credentials")
            return True
            
        except Exception as e:
            print(f"Firebase initialization failed: {e}")
            print("Running without Firebase support - user profile features will be disabled")
            return False

    def _check_firebase_available(self):
        """Check if Firebase is available"""
        if not self._firebase_available:
            print("Firebase is not available - operation skipped")
            return False
        return True

    async def save_user_profile(self, user_id: str, profile_data: Dict[str, Any]) -> bool:
        """Save user profile to Firestore"""
        if not self._check_firebase_available():
            return False
            
        try:
            profile_data['createdAt'] = datetime.utcnow()
            profile_data['updatedAt'] = datetime.utcnow()
            
            doc_ref = self._db.collection('user_profiles').document(user_id)
            doc_ref.set(profile_data)
            return True
        except Exception as e:
            print(f"Error saving user profile: {e}")
            return False

    async def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user profile from Firestore"""
        if not self._check_firebase_available():
            return None
            
        try:
            doc_ref = self._db.collection('user_profiles').document(user_id)
            doc = doc_ref.get()
            
            if doc.exists:
                data = doc.to_dict()
                data['id'] = doc.id
                return data
            return None
        except Exception as e:
            print(f"Error getting user profile: {e}")
            return None

    async def update_user_profile(self, user_id: str, profile_data: Dict[str, Any]) -> bool:
        """Update user profile in Firestore"""
        if not self._check_firebase_available():
            return False
            
        try:
            profile_data['updatedAt'] = datetime.utcnow()
            
            doc_ref = self._db.collection('user_profiles').document(user_id)
            doc_ref.update(profile_data)
            return True
        except Exception as e:
            print(f"Error updating user profile: {e}")
            return False

    async def delete_user_profile(self, user_id: str) -> bool:
        """Delete user profile from Firestore"""
        if not self._check_firebase_available():
            return False
            
        try:
            doc_ref = self._db.collection('user_profiles').document(user_id)
            doc_ref.delete()
            return True
        except Exception as e:
            print(f"Error deleting user profile: {e}")
            return False

    async def get_all_user_profiles(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all user profiles with pagination"""
        if not self._check_firebase_available():
            return []
            
        try:
            docs = self._db.collection('user_profiles').limit(limit).stream()
            profiles = []
            
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                profiles.append(data)
            
            return profiles
        except Exception as e:
            print(f"Error getting all user profiles: {e}")
            return []

    async def verify_id_token(self, id_token: str) -> Optional[Dict[str, Any]]:
        """Verify Firebase ID token"""
        if not self._check_firebase_available():
            return None
            
        try:
            decoded_token = auth.verify_id_token(id_token)
            return decoded_token
        except Exception as e:
            print(f"Error verifying ID token: {e}")
            return None

    @property
    def is_available(self) -> bool:
        """Check if Firebase service is available"""
        return self._firebase_available


# Global instance
firebase_service = FirebaseService()
