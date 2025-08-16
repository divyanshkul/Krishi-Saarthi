import 'package:flutter/material.dart';
import '../services/audio_processing_service.dart';
import '../models/chat_response_model.dart';

enum TextProcessingState { idle, processing, success, error }

class TextProvider with ChangeNotifier {
  String _currentText = '';
  TextProcessingState _processingState = TextProcessingState.idle;
  ChatResponseModel? _lastResponse;
  String? _processingError;

  final AudioProcessingService _audioProcessingService = AudioProcessingService();

  String get currentText => _currentText;
  TextProcessingState get processingState => _processingState;
  ChatResponseModel? get lastResponse => _lastResponse;
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
    _lastResponse = null;
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
      
      if (result != null && result['success'] == true && result['response'] != null) {
        _lastResponse = ChatResponseModel.fromJson(result['response']);
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
    _lastResponse = null;
    _processingError = null;
    notifyListeners();
  }
}