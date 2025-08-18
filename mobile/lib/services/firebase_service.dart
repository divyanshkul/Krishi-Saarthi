import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:firebase_auth/firebase_auth.dart';
import '../models/user_profile.dart';
import '../models/crop.dart';

class FirebaseService {
  static final FirebaseFirestore _firestore = FirebaseFirestore.instance;
  static final FirebaseAuth _auth = FirebaseAuth.instance;

  static Future<String?> saveUserProfile(
    UserProfile userProfile,
    Crop crop,
  ) async {
    try {
      // Create anonymous user if not authenticated
      if (_auth.currentUser == null) {
        await _auth.signInAnonymously();
      }

      String userId = _auth.currentUser!.uid;

      // Use batch write for atomic operation
      WriteBatch batch = _firestore.batch();

      // Save farmer profile
      DocumentReference farmerRef = _firestore
          .collection('farmers')
          .doc(userId);
      batch.set(farmerRef, userProfile.toJson());

      // Save crop under farmers/{farmerId}/crops subcollection
      DocumentReference cropRef = farmerRef.collection('crops').doc();
      batch.set(cropRef, crop.toJson());

      await batch.commit();

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
          .collection('farmers')
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

  static Future<List<Crop>> getUserCrops() async {
    try {
      if (_auth.currentUser == null) return [];

      String userId = _auth.currentUser!.uid;
      QuerySnapshot snapshot = await _firestore
          .collection('farmers')
          .doc(userId)
          .collection('crops')
          .get();

      return snapshot.docs
          .map(
            (doc) => Crop.fromJson(doc.data() as Map<String, dynamic>, doc.id),
          )
          .toList();
    } catch (e) {
      print('Error getting user crops: $e');
      return [];
    }
  }

  static Future<bool> addCrop(Crop crop) async {
    try {
      if (_auth.currentUser == null) return false;

      String userId = _auth.currentUser!.uid;
      await _firestore
          .collection('farmers')
          .doc(userId)
          .collection('crops')
          .add(crop.toJson());

      return true;
    } catch (e) {
      print('Error adding crop: $e');
      return false;
    }
  }

  static Future<bool> deleteCrop(String cropId) async {
    try {
      if (_auth.currentUser == null) return false;

      String userId = _auth.currentUser!.uid;
      await _firestore
          .collection('farmers')
          .doc(userId)
          .collection('crops')
          .doc(cropId)
          .delete();

      return true;
    } catch (e) {
      print('Error deleting crop: $e');
      return false;
    }
  }

  static Future<bool> updateUserProfile(UserProfile userProfile) async {
    try {
      if (_auth.currentUser == null) return false;

      String userId = _auth.currentUser!.uid;
      await _firestore
          .collection('farmers')
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

  // Legacy support for old schema migration
  static Future<void> migrateOldUserProfile() async {
    try {
      if (_auth.currentUser == null) return;

      String userId = _auth.currentUser!.uid;

      // Check if old profile exists
      DocumentSnapshot oldDoc = await _firestore
          .collection('user_profiles')
          .doc(userId)
          .get();

      if (oldDoc.exists) {
        final oldData = oldDoc.data() as Map<String, dynamic>;

        // Create new user profile without crop field
        UserProfile newProfile = UserProfile(
          name: oldData['name'],
          age: oldData['age'],
          gender: oldData['gender'],
          landHolding: oldData['landHolding'],
          district: oldData['district'] ?? 'Unknown',
          state: oldData['state'] ?? 'Unknown',
          caste: oldData['caste'],
          income: oldData['income'],
          createdAt: DateTime.parse(oldData['createdAt']),
        );

        // Create crop from old profile
        Crop crop = Crop(
          cropType: oldData['crop'] ?? 'Mixed',
          variety: 'Standard',
          sowingDate: DateTime.now().subtract(Duration(days: 30)),
          district: oldData['district'] ?? 'Unknown',
          state: oldData['state'] ?? 'Unknown',
        );

        // Save to new schema
        await saveUserProfile(newProfile, crop);

        // Delete old profile
        await _firestore.collection('user_profiles').doc(userId).delete();

        print('Successfully migrated user profile to new schema');
      }
    } catch (e) {
      print('Error migrating user profile: $e');
    }
  }
}
