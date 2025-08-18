import 'dart:convert';
import 'package:http/http.dart' as http;
import '../config/api_config.dart';
import '../models/video_recommendation.dart';

class YouTubeApiService {
  static String get baseUrl => ApiConfig.baseUrl;

  static Future<List<VideoRecommendation>> getVideoRecommendations(
    String farmerId,
  ) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/youtube/farmer/$farmerId/videos'),
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        if (data['success'] == true) {
          final List<dynamic> videos = data['videos'];
          return videos
              .map((video) => VideoRecommendation.fromJson(video))
              .toList();
        }
      }

      throw Exception('Failed to load video recommendations');
    } catch (e) {
      print('Error fetching video recommendations: $e');
      // Fallback to educational videos if API fails
      return getEducationalFallbackVideos();
    }
  }

  static Future<List<VideoRecommendation>> searchVideosByKeywords(
    List<String> keywords, {
    int maxResults = 10,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/youtube/search/keywords'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({'keywords': keywords, 'max_results': maxResults}),
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        if (data['success'] == true) {
          final List<dynamic> videos = data['videos'];
          return videos
              .map((video) => VideoRecommendation.fromJson(video))
              .toList();
        }
      }

      throw Exception('Failed to search videos');
    } catch (e) {
      print('Error searching videos: $e');
      // Fallback to educational videos if API fails
      return getEducationalFallbackVideos();
    }
  }

  /// Get curated educational fallback videos
  static List<VideoRecommendation> getEducationalFallbackVideos() {
    return [
      VideoRecommendation(
        title: 'Top 10 Natural Farming Techniques in Hindi',
        url: 'https://www.youtube.com/watch?v=pwZOHg55oqk',
        thumbnail: 'https://img.youtube.com/vi/pwZOHg55oqk/hqdefault.jpg',
        duration: '10:00 (approx.)',
        channel: 'Unknown', // As per YouTube metadata
      ),
      VideoRecommendation(
        title: 'कृषि दर्शन–ड्रिप सिंचाई प्रणाली | DD Kisan',
        url: 'https://www.youtube.com/watch?v=VMBZwW0vIfU',
        thumbnail: 'https://img.youtube.com/vi/VMBZwW0vIfU/hqdefault.jpg',
        duration: 'xx:xx',
        channel: 'DD Kisan',
      ),
      VideoRecommendation(
        title: 'PQNK – Pristine Organic Farming System (Hindi)',
        url: 'https://www.youtube.com/watch?v=0ijz2-3u870',
        thumbnail: 'https://img.youtube.com/vi/0ijz2-3u870/hqdefault.jpg',
        duration: 'xx:xx',
        channel: 'Unknown',
      ),
      VideoRecommendation(
        title: 'सिंचाई विधियों के प्रकार || Methods of Irrigation || UPCATET',
        url: 'https://www.youtube.com/watch?v=XMPD8n5ByJo',
        thumbnail: 'https://img.youtube.com/vi/XMPD8n5ByJo/hqdefault.jpg',
        duration: 'xx:xx',
        channel: 'Unknown',
      ),
      VideoRecommendation(
        title: 'ड्रिप इरिगेशन || Drip Irrigation System Full Information',
        url: 'https://www.youtube.com/watch?v=dv5m1RaIM1M',
        thumbnail: 'https://img.youtube.com/vi/dv5m1RaIM1M/hqdefault.jpg',
        duration: 'xx:xx',
        channel: 'Unknown',
      ),
    ];
  }
}
