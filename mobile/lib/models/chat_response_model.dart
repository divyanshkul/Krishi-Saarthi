import 'package:youtube_player_flutter/youtube_player_flutter.dart';

class ChatResponseModel {
  final String text;
  final String? videoUrl;
  final String? videoTitle;
  final String? websiteUrl;
  final String? websiteTitle;

  const ChatResponseModel({
    required this.text,
    this.videoUrl,
    this.videoTitle,
    this.websiteUrl,
    this.websiteTitle,
  });

  factory ChatResponseModel.fromJson(Map<String, dynamic> json) {
    return ChatResponseModel(
      text: json['text'] ?? '',
      videoUrl: json['video_url'],
      videoTitle: json['video_title'],
      websiteUrl: json['website_url'],
      websiteTitle: json['website_title'],
    );
  }

  bool get hasVideo => videoUrl != null && videoUrl!.isNotEmpty;
  bool get hasWebsite => websiteUrl != null && websiteUrl!.isNotEmpty;

  String? get videoId {
    if (!hasVideo) return null;
    return YoutubePlayer.convertUrlToId(videoUrl!);
  }
}