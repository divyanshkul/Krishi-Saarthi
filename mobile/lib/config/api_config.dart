import 'package:flutter_dotenv/flutter_dotenv.dart';

class ApiConfig {
  static String get baseUrl =>
      dotenv.env['BASE_URL'] ?? 'http://10.0.2.2:8000/api';
  static int get apiTimeout =>
      int.tryParse(dotenv.env['API_TIMEOUT'] ?? '120000') ?? 120000;

  static String get healthEndpoint => '$baseUrl/health';
  static String get chatEndpoint => '$baseUrl/chat';
  static String get mandiEndpoint => '$baseUrl/mandi';
  static String get schemesEndpoint => '$baseUrl/schemes';
  static String get visionEndpoint => '$baseUrl/vision';

  static String get processAudioEndpoint => '$baseUrl/chat/process-audio';
  static String get processTextEndpoint => '$baseUrl/chat/process-text';

  // Helper method to build full API URLs
  static String buildUrl(String endpoint) {
    return '$baseUrl$endpoint';
  }

  // Debug method to check current environment
  static void debugConfig() {
    print('🌐 API Config:');
    print('Base URL: $baseUrl');
    print('Timeout: ${apiTimeout}ms');
  }
}
