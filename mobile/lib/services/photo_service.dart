import 'dart:io';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:path_provider/path_provider.dart';
import 'package:permission_handler/permission_handler.dart';
import 'package:path/path.dart' as path;

class PhotoService {
  final ImagePicker _picker = ImagePicker();

  Future<String?> capturePhoto() async {
    try {
      final hasPermission = await _requestCameraPermission();
      if (!hasPermission) {
        throw Exception('Camera permission denied');
      }

      final XFile? photo = await _picker.pickImage(
        source: ImageSource.camera,
        maxWidth: 1920,
        maxHeight: 1080,
        imageQuality: 85,
      );

      if (photo != null) {
        return await _savePhoto(photo);
      }
      return null;
    } catch (e) {
      debugPrint('Error capturing photo: $e');
      rethrow;
    }
  }

  Future<String?> selectFromGallery() async {
    try {
      final hasPermission = await _requestStoragePermission();
      if (!hasPermission) {
        throw Exception('Storage permission denied');
      }

      final XFile? photo = await _picker.pickImage(
        source: ImageSource.gallery,
        maxWidth: 1920,
        maxHeight: 1080,
        imageQuality: 85,
      );

      if (photo != null) {
        return await _savePhoto(photo);
      }
      return null;
    } catch (e) {
      debugPrint('Error selecting photo from gallery: $e');
      rethrow;
    }
  }

  Future<String> _savePhoto(XFile photo) async {
    final Directory appDocDir = await getApplicationDocumentsDirectory();
    final String photoDir = path.join(appDocDir.path, 'photos');
    
    final Directory photosDirectory = Directory(photoDir);
    if (!await photosDirectory.exists()) {
      await photosDirectory.create(recursive: true);
    }

    final DateTime now = DateTime.now();
    final String timestamp = "${now.year}-${now.month.toString().padLeft(2, '0')}-${now.day.toString().padLeft(2, '0')}_${now.hour.toString().padLeft(2, '0')}-${now.minute.toString().padLeft(2, '0')}-${now.second.toString().padLeft(2, '0')}";
    final String extension = path.extension(photo.path);
    final String fileName = 'photo_$timestamp$extension';
    final String savedPath = path.join(photoDir, fileName);

    final File sourceFile = File(photo.path);
    await sourceFile.copy(savedPath);

    debugPrint('Photo saved to: $savedPath');
    return savedPath;
  }

  Future<bool> _requestCameraPermission() async {
    final PermissionStatus status = await Permission.camera.request();
    return status.isGranted;
  }

  Future<bool> _requestStoragePermission() async {
    final PermissionStatus status = await Permission.storage.request();
    return status.isGranted;
  }

  Future<void> deletePhoto(String photoPath) async {
    try {
      final File photoFile = File(photoPath);
      if (await photoFile.exists()) {
        await photoFile.delete();
        debugPrint('Photo deleted: $photoPath');
      }
    } catch (e) {
      debugPrint('Error deleting photo: $e');
    }
  }
}