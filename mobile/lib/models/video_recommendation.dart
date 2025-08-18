class VideoRecommendation {
  final String title;
  final String url;
  final String? thumbnail;
  final String? duration;
  final String? channel;

  VideoRecommendation({
    required this.title,
    required this.url,
    this.thumbnail,
    this.duration,
    this.channel,
  });

  factory VideoRecommendation.fromJson(Map<String, dynamic> json) {
    return VideoRecommendation(
      title: json['title'] ?? '',
      url: json['url'] ?? '',
      thumbnail: json['thumbnail'],
      duration: json['duration'],
      channel: json['channel'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'title': title,
      'url': url,
      'thumbnail': thumbnail,
      'duration': duration,
      'channel': channel,
    };
  }

  String? get videoId {
    // Extract YouTube video ID from URL
    final regex = RegExp(r'(?:youtube\.com\/watch\?v=|youtu\.be\/)([^&\n?#]+)');
    final match = regex.firstMatch(url);
    return match?.group(1);
  }
}
