import 'package:flutter/material.dart';
import '../widgets/agricultural_news_card.dart';
import '../widgets/app_header.dart';
import '../widgets/government_schemes_card.dart';
import '../widgets/video_carousel.dart';

class ForYouPage extends StatelessWidget {
  const ForYouPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Column(
        children: [
          const AppHeader(),
          Expanded(
            child: ListView(
              padding: const EdgeInsets.all(12.0),
              children: [
                _buildVideoRecommendationsCard(),
                const SizedBox(height: 12),
                const GovernmentSchemesCard(),
                const SizedBox(height: 12),
                const AgriculturalNewsCard(),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildVideoRecommendationsCard() {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.red.shade50,
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: const [
          Padding(
            padding: EdgeInsets.symmetric(horizontal: 4.0),
            child: Text(
              'Video Recommendations',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
          ),
          SizedBox(height: 8),
          VideoCarousel(),
        ],
      ),
    );
  }
}
