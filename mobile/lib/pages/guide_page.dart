import 'package:flutter/material.dart';
import '../widgets/app_header.dart';

class GuidePage extends StatelessWidget {
  const GuidePage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Column(
        children: [
          const AppHeader(),
          const SizedBox(height: 8),
          Expanded(
            child: ListView(
              padding: const EdgeInsets.all(12),
              children: [
                _buildSoilCard(),
                const SizedBox(height: 12),
                _buildAfterHarvestCard(),
                const SizedBox(height: 12),
                _buildPreparingCard(),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSoilCard() {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.green.shade50,
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Row(
                children: const [
                  Icon(Icons.spa),
                  SizedBox(width: 8),
                  Text(
                    'Soil Preparation',
                    style: TextStyle(fontWeight: FontWeight.bold),
                  ),
                ],
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                decoration: BoxDecoration(
                  color: Colors.orange.shade200,
                  borderRadius: BorderRadius.circular(8),
                ),
                child: const Text('Active'),
              ),
            ],
          ),
          const SizedBox(height: 8),
          const Text(
            'AI Suggestion: Deep plowing is recommended for your area. Moisture level is 18% suitable.',
          ),
          const SizedBox(height: 8),
          Row(
            children: [
              ElevatedButton.icon(
                onPressed: () {},
                icon: const Icon(Icons.play_circle),
                label: const Text('Watch Video'),
              ),
              const SizedBox(width: 8),
              OutlinedButton(
                onPressed: () {},
                child: const Text('Detailed Guide'),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildAfterHarvestCard() {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        boxShadow: [BoxShadow(color: Colors.black12, blurRadius: 6)],
      ),
      child: const ListTile(
        title: Text('Post-Harvest'),
        subtitle: Text('Storage, processing and marketing strategy'),
      ),
    );
  }

  Widget _buildPreparingCard() {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.green.shade50,
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        children: const [
          Icon(Icons.autorenew),
          SizedBox(width: 8),
          Expanded(
            child: Text(
              'AI is preparing personalized suggestions for your farm...',
            ),
          ),
        ],
      ),
    );
  }
}
