import 'package:flutter/material.dart';

class GuidanceTopic {
  final String title;
  final String icon;
  final String description;
  final List<String> videoLinks;
  final List<String> articles;

  GuidanceTopic({
    required this.title,
    required this.icon,
    required this.description,
    this.videoLinks = const [],
    this.articles = const [],
  });

  factory GuidanceTopic.fromJson(Map<String, dynamic> json) {
    return GuidanceTopic(
      title: json['title'] ?? '',
      icon: json['icon'] ?? 'help',
      description: json['description'] ?? '',
      videoLinks: List<String>.from(json['video_links'] ?? []),
      articles: List<String>.from(json['articles'] ?? []),
    );
  }

  bool get hasActions => videoLinks.isNotEmpty || articles.isNotEmpty;

  /// Convert icon string to Flutter IconData
  IconData get iconData {
    switch (icon.toLowerCase()) {
      case 'plow':
      case 'agriculture':
        return Icons.agriculture;
      case 'science':
        return Icons.science;
      case 'schedule':
        return Icons.schedule;
      case 'grain':
        return Icons.grain;
      case 'water_drop':
        return Icons.water_drop;
      case 'eco':
        return Icons.eco;
      case 'bug_report':
        return Icons.bug_report;
      case 'visibility':
        return Icons.visibility;
      case 'cut':
        return Icons.cut;
      case 'inventory':
        return Icons.inventory;
      case 'trending_up':
        return Icons.trending_up;
      default:
        return Icons.help;
    }
  }
}

class StageGuidance {
  final String stageName;
  final String stageType;
  final List<GuidanceTopic> topics;

  StageGuidance({
    required this.stageName,
    required this.stageType,
    required this.topics,
  });

  factory StageGuidance.fromJson(Map<String, dynamic> json) {
    return StageGuidance(
      stageName: json['stage_name'] ?? '',
      stageType: json['stage_type'] ?? '',
      topics: (json['topics'] as List? ?? [])
          .map((topic) => GuidanceTopic.fromJson(topic))
          .toList(),
    );
  }
}

class GuidedModeResponse {
  final bool success;
  final String cropName;
  final Map<String, StageGuidance> stages;
  final String timestamp;
  final String? error;

  GuidedModeResponse({
    required this.success,
    required this.cropName,
    required this.stages,
    required this.timestamp,
    this.error,
  });

  factory GuidedModeResponse.fromJson(Map<String, dynamic> json) {
    final stagesMap = <String, StageGuidance>{};

    if (json['stages'] != null) {
      (json['stages'] as Map<String, dynamic>).forEach((key, value) {
        stagesMap[key] = StageGuidance.fromJson(value);
      });
    }

    return GuidedModeResponse(
      success: json['success'] ?? false,
      cropName: json['crop_name'] ?? '',
      stages: stagesMap,
      timestamp: json['timestamp'] ?? '',
      error: json['error'],
    );
  }

  /// Get stage guidance by stage number (1-5)
  StageGuidance? getStageByNumber(int stageNumber) {
    switch (stageNumber) {
      case 1:
        return stages['soilPrep'];
      case 2:
        return stages['seedSowing'];
      case 3:
        return stages['cropGrowth'];
      case 4:
        return stages['harvesting'];
      case 5:
        return stages['postHarvest'];
      default:
        return null;
    }
  }

  /// Check if the response has valid data
  bool get hasValidData => success && stages.isNotEmpty;
}
