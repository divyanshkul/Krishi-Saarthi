import 'package:flutter/material.dart';
import '../services/audio_processing_service.dart';

enum TextProcessingState { idle, processing, success, error }

class TextProvider with ChangeNotifier {
  String _currentText = '';
  TextProcessingState _processingState = TextProcessingState.idle;
  String? _aiResponse;
  String? _processingError;

  final AudioProcessingService _audioProcessingService = AudioProcessingService();

  String get currentText => _currentText;
  TextProcessingState get processingState => _processingState;
  String? get aiResponse => _aiResponse;
  String? get processingError => _processingError;
  bool get isProcessing => _processingState == TextProcessingState.processing;
  bool get hasText => _currentText.trim().isNotEmpty;

  void setText(String text) {
    _currentText = text;
    notifyListeners();
  }

  void clearText() {
    _currentText = '';
    _processingState = TextProcessingState.idle;
    _aiResponse = null;
    _processingError = null;
    notifyListeners();
  }

  Future<void> processText([String? imagePath]) async {
    if (!hasText) {
      _processingError = 'No text to process';
      _processingState = TextProcessingState.error;
      notifyListeners();
      return;
    }

    try {
      _processingState = TextProcessingState.processing;
      _processingError = null;
      notifyListeners();

      final result = await _audioProcessingService.processText(_currentText, imagePath);
      
      if (result != null && result['success'] == true) {
        _aiResponse = result['response'] ?? 'No response received';
        _processingState = TextProcessingState.success;
        
        // Clear text after successful processing
        _currentText = '';
      } else {
        _processingError = result?['detail'] ?? 'Processing failed';
        _processingState = TextProcessingState.error;
      }
    } catch (e) {
      _processingError = e.toString();
      _processingState = TextProcessingState.error;
    }

    notifyListeners();
  }

  void clearProcessing() {
    _processingState = TextProcessingState.idle;
    _aiResponse = null;
    _processingError = null;
    notifyListeners();
  }
}