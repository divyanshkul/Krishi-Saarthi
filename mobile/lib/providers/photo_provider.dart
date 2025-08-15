import 'dart:io';
import 'package:flutter/material.dart';
import '../services/photo_service.dart';

class PhotoProvider with ChangeNotifier {
  String? _currentPhotoPath;
  bool _hasPhoto = false;
  
  final PhotoService _photoService = PhotoService();

  String? get currentPhotoPath => _currentPhotoPath;
  bool get hasPhoto => _hasPhoto;

  void setPhoto(String photoPath) {
    _currentPhotoPath = photoPath;
    _hasPhoto = true;
    notifyListeners();
  }

  void clearPhoto() {
    if (_currentPhotoPath != null) {
      _photoService.deletePhoto(_currentPhotoPath!);
    }
    _currentPhotoPath = null;
    _hasPhoto = false;
    notifyListeners();
  }

  Future<bool> capturePhoto() async {
    try {
      final String? photoPath = await _photoService.capturePhoto();
      if (photoPath != null) {
        setPhoto(photoPath);
        return true;
      }
      return false;
    } catch (e) {
      debugPrint('Error capturing photo: $e');
      return false;
    }
  }

  Future<bool> selectFromGallery() async {
    try {
      final String? photoPath = await _photoService.selectFromGallery();
      if (photoPath != null) {
        setPhoto(photoPath);
        return true;
      }
      return false;
    } catch (e) {
      debugPrint('Error selecting photo from gallery: $e');
      return false;
    }
  }

  String? getPhotoDisplayName() {
    if (_currentPhotoPath == null) return null;
    
    final fileName = _currentPhotoPath!.split('/').last;
    final parts = fileName.replaceAll('photo_', '').split('.');
    
    try {
      if (parts.isNotEmpty) {
        final namePart = parts[0];
        final dateTimeParts = namePart.split('_');
        
        if (dateTimeParts.length == 2) {
          final datePart = dateTimeParts[0];
          final timePart = dateTimeParts[1].replaceAll('-', ':');
          
          final dateComponents = datePart.split('-');
          final timeComponents = timePart.split(':');
          
          if (dateComponents.length == 3 && timeComponents.length == 3) {
            final capturedDateTime = DateTime(
              int.parse(dateComponents[0]),
              int.parse(dateComponents[1]),
              int.parse(dateComponents[2]),
              int.parse(timeComponents[0]),
              int.parse(timeComponents[1]),
              int.parse(timeComponents[2]),
            );
            
            final now = DateTime.now();
            final difference = now.difference(capturedDateTime);
            
            if (difference.inMinutes < 1) {
              return 'Just taken';
            } else if (difference.inHours < 1) {
              return '${difference.inMinutes}m ago';
            } else if (difference.inDays < 1) {
              return '${difference.inHours}h ago';
            } else {
              return '${difference.inDays}d ago';
            }
          }
        }
      }
      return 'Photo attached';
    } catch (e) {
      return 'Photo attached';
    }
  }

  File? getPhotoFile() {
    if (_currentPhotoPath == null) return null;
    return File(_currentPhotoPath!);
  }
}