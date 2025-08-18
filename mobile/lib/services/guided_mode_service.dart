import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter/foundation.dart';
import '../config/api_config.dart';
import '../models/guided_mode.dart';

class GuidedModeService {
  static final GuidedModeService _instance = GuidedModeService._internal();
  factory GuidedModeService() => _instance;
  GuidedModeService._internal();

  /// Get comprehensive agricultural guidance for a specific crop
  Future<GuidedModeResponse?> getCropGuidance(
    String cropName, {
    String? farmerId,
  }) async {
    try {
      debugPrint('🌾 Fetching guidance for crop: $cropName');

      // Build URL with optional farmer_id parameter
      String url =
          '${ApiConfig.guidedModeEndpoint}/${Uri.encodeComponent(cropName)}';
      if (farmerId != null && farmerId.isNotEmpty) {
        url += '?farmer_id=${Uri.encodeComponent(farmerId)}';
      }

      final response = await http
          .get(Uri.parse(url), headers: {'Content-Type': 'application/json'})
          .timeout(Duration(milliseconds: ApiConfig.apiTimeout));

      if (response.statusCode == 200) {
        debugPrint('✅ Successfully received crop guidance');
        final jsonData = json.decode(response.body);
        return GuidedModeResponse.fromJson(jsonData);
      } else {
        debugPrint('❌ Failed to get crop guidance: ${response.statusCode}');
        debugPrint('Response body: ${response.body}');
        return null;
      }
    } catch (e) {
      debugPrint('❌ Error fetching crop guidance: $e');
      return null;
    }
  }

  /// Check the health status of the guided mode service
  Future<bool> checkServiceHealth() async {
    try {
      final response = await http
          .get(
            Uri.parse(ApiConfig.guidedModeHealthEndpoint),
            headers: {'Content-Type': 'application/json'},
          )
          .timeout(
            Duration(milliseconds: 10000),
          ); // 10 second timeout for health check

      if (response.statusCode == 200) {
        final jsonData = json.decode(response.body);
        return jsonData['status'] == 'healthy' ||
            jsonData['status'] == 'degraded';
      }

      return false;
    } catch (e) {
      debugPrint('Health check failed: $e');
      return false;
    }
  }

  /// Get fallback guidance when API is not available
  static GuidedModeResponse getFallbackGuidance(String cropName) {
    return GuidedModeResponse(
      success: true,
      cropName: cropName,
      timestamp: DateTime.now().toIso8601String(),
      stages: {
        'soilPrep': StageGuidance(
          stageName: 'Soil Preparation',
          stageType: 'soil_preparation',
          topics: [
            GuidanceTopic(
              title: 'Basic Soil Preparation',
              icon: 'plow',
              description:
                  'Prepare soil for $cropName by plowing to appropriate depth (15-20 cm) and ensuring proper drainage. Test soil pH and add organic matter to improve soil health.',
              videoLinks: [],
              articles: [],
            ),
            GuidanceTopic(
              title: 'Soil Health Management',
              icon: 'science',
              description:
                  'Conduct soil testing to understand nutrient requirements for $cropName. Add compost or farmyard manure to improve soil structure and fertility.',
              videoLinks: [],
              articles: [],
            ),
          ],
        ),
        'seedSowing': StageGuidance(
          stageName: 'Seed Sowing',
          stageType: 'seed_sowing',
          topics: [
            GuidanceTopic(
              title: 'Sowing Guidelines',
              icon: 'grain',
              description:
                  'Follow recommended sowing practices for $cropName including proper spacing, depth, and timing. Use quality seeds and treat them before sowing.',
              videoLinks: [],
              articles: [],
            ),
            GuidanceTopic(
              title: 'Seed Treatment',
              icon: 'science',
              description:
                  'Treat seeds with appropriate fungicides to prevent soil-borne diseases. Follow recommended seed rate for optimal plant population of $cropName.',
              videoLinks: [],
              articles: [],
            ),
          ],
        ),
        'cropGrowth': StageGuidance(
          stageName: 'Crop Growth Management',
          stageType: 'crop_growth',
          topics: [
            GuidanceTopic(
              title: 'Irrigation Management',
              icon: 'water_drop',
              description:
                  'Provide adequate water to $cropName at critical growth stages. Monitor soil moisture and avoid water stress during flowering and grain filling.',
              videoLinks: [],
              articles: [],
            ),
            GuidanceTopic(
              title: 'Nutrient Management',
              icon: 'eco',
              description:
                  'Apply balanced fertilizers based on soil test recommendations for $cropName. Use organic sources like compost to supplement chemical fertilizers.',
              videoLinks: [],
              articles: [],
            ),
            GuidanceTopic(
              title: 'Pest Management',
              icon: 'bug_report',
              description:
                  'Monitor $cropName regularly for pests and diseases. Use integrated pest management approaches including biological and chemical controls.',
              videoLinks: [],
              articles: [],
            ),
          ],
        ),
        'harvesting': StageGuidance(
          stageName: 'Harvesting',
          stageType: 'harvesting',
          topics: [
            GuidanceTopic(
              title: 'Harvest Timing',
              icon: 'cut',
              description:
                  'Harvest $cropName at optimal maturity for best quality and yield. Check for proper moisture content and visual indicators of maturity.',
              videoLinks: [],
              articles: [],
            ),
            GuidanceTopic(
              title: 'Harvesting Methods',
              icon: 'visibility',
              description:
                  'Use appropriate harvesting techniques for $cropName to minimize losses. Handle harvested produce carefully to maintain quality.',
              videoLinks: [],
              articles: [],
            ),
          ],
        ),
        'postHarvest': StageGuidance(
          stageName: 'Post-Harvest Management',
          stageType: 'post_harvest',
          topics: [
            GuidanceTopic(
              title: 'Storage Management',
              icon: 'inventory',
              description:
                  'Store $cropName properly to maintain quality and prevent losses. Use clean, dry storage facilities and monitor for pest infestation.',
              videoLinks: [],
              articles: [],
            ),
            GuidanceTopic(
              title: 'Market Planning',
              icon: 'trending_up',
              description:
                  'Plan marketing strategy for $cropName to get better prices. Monitor market prices and choose optimal timing for sale.',
              videoLinks: [],
              articles: ['Check government mandi prices and MSP information'],
            ),
          ],
        ),
      },
    );
  }
}
