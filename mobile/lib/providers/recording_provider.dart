import 'package:flutter/material.dart';

class RecordingProvider with ChangeNotifier {
  String? _currentRecordingPath;
  bool _hasRecording = false;

  String? get currentRecordingPath => _currentRecordingPath;
  bool get hasRecording => _hasRecording;

  void setRecording(String recordingPath) {
    _currentRecordingPath = recordingPath;
    _hasRecording = true;
    notifyListeners();
  }

  void clearRecording() {
    _currentRecordingPath = null;
    _hasRecording = false;
    notifyListeners();
  }

  String? getRecordingDisplayName() {
    if (_currentRecordingPath == null) return null;
    
    final fileName = _currentRecordingPath!.split('/').last;
    // Parse filename format: recording_2024-01-15_14-30-45.wav
    final parts = fileName.replaceAll('recording_', '').replaceAll('.wav', '').split('_');
    
    try {
      if (parts.length == 2) {
        final datePart = parts[0]; // 2024-01-15
        final timePart = parts[1].replaceAll('-', ':'); // 14:30:45
        
        final dateComponents = datePart.split('-');
        final timeComponents = timePart.split(':');
        
        if (dateComponents.length == 3 && timeComponents.length == 3) {
          final recordedDateTime = DateTime(
            int.parse(dateComponents[0]), // year
            int.parse(dateComponents[1]), // month
            int.parse(dateComponents[2]), // day
            int.parse(timeComponents[0]), // hour
            int.parse(timeComponents[1]), // minute
            int.parse(timeComponents[2]), // second
          );
          
          final now = DateTime.now();
          final difference = now.difference(recordedDateTime);
          
          if (difference.inMinutes < 1) {
            return 'Just recorded';
          } else if (difference.inHours < 1) {
            return '${difference.inMinutes}m ago';
          } else if (difference.inDays < 1) {
            return '${difference.inHours}h ago';
          } else {
            return '${difference.inDays}d ago';
          }
        }
      }
      return 'Audio recording';
    } catch (e) {
      return 'Audio recording';
    }
  }
}