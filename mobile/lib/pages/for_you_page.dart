import 'package:flutter/material.dart';
import '../widgets/app_header.dart';
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
                _buildGovtSchemesCard(),
                const SizedBox(height: 12),
                _buildNewsCard(),
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

  Widget _buildGovtSchemesCard() {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.orange.shade50,
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Government Schemes',
            style: TextStyle(fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 8),
          ListTile(
            leading: const Icon(Icons.account_balance_wallet),
            title: const Text('PM-KISAN'),
            subtitle: const Text(
              'You are eligible · Next installment: 15th August',
            ),
          ),
          const Divider(),
          ListTile(
            leading: const Icon(Icons.shield),
            title: const Text('Crop Insurance Scheme'),
            subtitle: const Text('Application deadline: 30th November'),
          ),
        ],
      ),
    );
  }

  Widget _buildNewsCard() {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        boxShadow: [BoxShadow(color: Colors.black12, blurRadius: 6)],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: const [
          Text(
            'Agriculture News',
            style: TextStyle(fontWeight: FontWeight.bold),
          ),
          SizedBox(height: 8),
          ListTile(
            title: Text('5% increase in MSP for Rabi crops'),
            subtitle: Text('Ministry of Agriculture · 2 hours ago'),
          ),
          ListTile(
            title: Text('Warning of seasonal rain in Madhya Pradesh'),
            subtitle: Text('Meteorological Department · 4 hours ago'),
          ),
        ],
      ),
    );
  }
}
