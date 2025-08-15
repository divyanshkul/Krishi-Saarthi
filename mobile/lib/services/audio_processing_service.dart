import 'dart:io';
import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import '../config/api_config.dart';

class AudioProcessingService {
  static final AudioProcessingService _instance = AudioProcessingService._internal();
  factory AudioProcessingService() => _instance;
  AudioProcessingService._internal();

  final Dio _dio = Dio(BaseOptions(
    connectTimeout: Duration(milliseconds: ApiConfig.apiTimeout),
    receiveTimeout: Duration(milliseconds: ApiConfig.apiTimeout),
  ));

  Future<Map<String, dynamic>?> processAudio(String audioFilePath) async {
    try {
      debugPrint('🎵 Processing audio: $audioFilePath');
      
      // Check if file exists
      final audioFile = File(audioFilePath);
      if (!await audioFile.exists()) {
        throw Exception('Audio file not found: $audioFilePath');
      }

      // Create multipart form data
      final formData = FormData.fromMap({
        'audio_file': await MultipartFile.fromFile(
          audioFilePath,
          filename: audioFile.path.split('/').last,
        ),
      });

      debugPrint('🌐 Uploading to: ${ApiConfig.processAudioEndpoint}');

      // Send POST request
      final response = await _dio.post(
        ApiConfig.processAudioEndpoint,
        data: formData,
        options: Options(
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        ),
      );

      debugPrint('✅ Response: ${response.statusCode}');
      
      if (response.statusCode == 200) {
        final data = response.data as Map<String, dynamic>;
        debugPrint('📝 AI Response: ${data['response']}');
        return data;
      } else {
        throw Exception('Server returned ${response.statusCode}');
      }
      
    } on DioException catch (e) {
      debugPrint('❌ Dio Error: ${e.message}');
      if (e.response != null) {
        debugPrint('❌ Server Response: ${e.response?.data}');
        throw Exception('Server error: ${e.response?.data['detail'] ?? e.message}');
      } else {
        throw Exception('Network error: ${e.message}');
      }
    } catch (e) {
      debugPrint('❌ Error processing audio: $e');
      throw Exception('Failed to process audio: $e');
    }
  }

  Future<Map<String, dynamic>?> processText(String text, [String? imageFilePath]) async {
    try {
      debugPrint('📝 Processing text: $text');
      
      // Create form data
      final Map<String, dynamic> formFields = {'text': text};
      
      // Add image if provided
      if (imageFilePath != null) {
        final imageFile = File(imageFilePath);
        if (await imageFile.exists()) {
          formFields['image_file'] = await MultipartFile.fromFile(
            imageFilePath,
            filename: imageFile.path.split('/').last,
          );
        }
      }

      final formData = FormData.fromMap(formFields);

      debugPrint('🌐 Uploading to: ${ApiConfig.processTextEndpoint}');

      final response = await _dio.post(
        ApiConfig.processTextEndpoint,
        data: formData,
        options: Options(
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        ),
      );

      if (response.statusCode == 200) {
        final data = response.data as Map<String, dynamic>;
        debugPrint('📝 AI Response: ${data['response']}');
        return data;
      } else {
        throw Exception('Server returned ${response.statusCode}');
      }
      
    } on DioException catch (e) {
      debugPrint('❌ Dio Error: ${e.message}');
      if (e.response != null) {
        debugPrint('❌ Server Response: ${e.response?.data}');
        throw Exception('Server error: ${e.response?.data['detail'] ?? e.message}');
      } else {
        throw Exception('Network error: ${e.message}');
      }
    } catch (e) {
      debugPrint('❌ Error processing text: $e');
      throw Exception('Failed to process text: $e');
    }
  }
}