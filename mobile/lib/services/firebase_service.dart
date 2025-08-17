import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:firebase_auth/firebase_auth.dart';
import '../models/user_profile.dart';

class FirebaseService {
  static final FirebaseFirestore _firestore = FirebaseFirestore.instance;
  static final FirebaseAuth _auth = FirebaseAuth.instance;

  static Future<String?> saveUserProfile(UserProfile userProfile) async {
    try {
      // Create anonymous user if not authenticated
      if (_auth.currentUser == null) {
        await _auth.signInAnonymously();
      }

      String userId = _auth.currentUser!.uid;

      // Save to Firestore
      await _firestore
          .collection('user_profiles')
          .doc(userId)
          .set(userProfile.toJson());

      return userId;
    } catch (e) {
      print('Error saving user profile: $e');
      return null;
    }
  }

  static Future<UserProfile?> getUserProfile() async {
    try {
      if (_auth.currentUser == null) return null;

      String userId = _auth.currentUser!.uid;
      DocumentSnapshot doc = await _firestore
          .collection('user_profiles')
          .doc(userId)
          .get();

      if (doc.exists) {
        return UserProfile.fromJson(doc.data() as Map<String, dynamic>, doc.id);
      }
      return null;
    } catch (e) {
      print('Error getting user profile: $e');
      return null;
    }
  }

  static Future<bool> updateUserProfile(UserProfile userProfile) async {
    try {
      if (_auth.currentUser == null) return false;

      String userId = _auth.currentUser!.uid;
      await _firestore
          .collection('user_profiles')
          .doc(userId)
          .update(userProfile.toJson());

      return true;
    } catch (e) {
      print('Error updating user profile: $e');
      return false;
    }
  }

  static String? getCurrentUserId() {
    return _auth.currentUser?.uid;
  }

  static Future<void> signOut() async {
    await _auth.signOut();
  }
}
