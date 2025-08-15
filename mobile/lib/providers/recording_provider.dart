import 'package:flutter/material.dart';
import '../services/audio_processing_service.dart';

enum ProcessingState { idle, processing, success, error }

class RecordingProvider with ChangeNotifier {
  String? _currentRecordingPath;
  bool _hasRecording = false;
  ProcessingState _processingState = ProcessingState.idle;
  String? _aiResponse;
  String? _processingError;

  final AudioProcessingService _audioProcessingService = AudioProcessingService();

  String? get currentRecordingPath => _currentRecordingPath;
  bool get hasRecording => _hasRecording;
  ProcessingState get processingState => _processingState;
  String? get aiResponse => _aiResponse;
  String? get processingError => _processingError;
  bool get isProcessing => _processingState == ProcessingState.processing;

  void setRecording(String recordingPath) {
    _currentRecordingPath = recordingPath;
    _hasRecording = true;
    notifyListeners();
  }

  void clearRecording() {
    _currentRecordingPath = null;
    _hasRecording = false;
    _processingState = ProcessingState.idle;
    _aiResponse = null;
    _processingError = null;
    notifyListeners();
  }

  Future<void> processAudio([String? imagePath]) async {
    if (_currentRecordingPath == null) {
      _processingError = 'No recording to process';
      _processingState = ProcessingState.error;
      notifyListeners();
      return;
    }

    try {
      _processingState = ProcessingState.processing;
      _processingError = null;
      notifyListeners();

      final result = await _audioProcessingService.processAudio(_currentRecordingPath!, imagePath);
      
      if (result != null && result['success'] == true) {
        _aiResponse = result['response'] ?? 'No response received';
        _processingState = ProcessingState.success;
        
        // Clear recording after successful processing
        _currentRecordingPath = null;
        _hasRecording = false;
      } else {
        _processingError = result?['detail'] ?? 'Processing failed';
        _processingState = ProcessingState.error;
      }
    } catch (e) {
      _processingError = e.toString();
      _processingState = ProcessingState.error;
    }

    notifyListeners();
  }

  void clearProcessing() {
    _processingState = ProcessingState.idle;
    _aiResponse = null;
    _processingError = null;
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