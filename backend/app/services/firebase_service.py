
import firebase_admin
from firebase_admin import credentials, firestore
import os
from typing import Optional, Dict, Any

class FirebaseService:
	def __init__(self):
		if not firebase_admin._apps:
			cred_path = os.getenv('FIREBASE_SERVICE_ACCOUNT_PATH')
			if cred_path and os.path.exists(cred_path):
				cred = credentials.Certificate(cred_path)
				firebase_admin.initialize_app(cred)
			else:
				firebase_admin.initialize_app()
		self._db = firestore.client()

	async def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
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

firebase_service = FirebaseService()


