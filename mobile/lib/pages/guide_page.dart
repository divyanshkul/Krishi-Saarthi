import 'package:flutter/material.dart';
import '../models/suggestion.dart';
import '../widgets/app_header.dart';
import '../widgets/stage_progress_bar.dart';
import '../widgets/suggestion_card.dart';

class GuidePage extends StatefulWidget {
  const GuidePage({super.key});

  @override
  State<GuidePage> createState() => _GuidePageState();
}

class _GuidePageState extends State<GuidePage> {
  int _currentStage = 1;

  void _onStageSelected(int stage) {
    setState(() {
      _currentStage = stage;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Column(
        children: [
          const AppHeader(),
          StageProgressBar(
            currentStage: _currentStage,
            onStageSelected: _onStageSelected,
          ),
          const SizedBox(height: 8),
          Expanded(
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16.0),
              child: _buildStageContent(_currentStage),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildStageContent(int stage) {
    final stageData = _getStageData(stage);
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.symmetric(vertical: 8.0),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                stageData['title']!,
                style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
              ),
              ElevatedButton.icon(
                onPressed: () {
                  // AI Suggestion Action
                },
                icon: const Icon(Icons.auto_awesome, size: 18),
                label: const Text('AI Suggestion'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.blue.shade700,
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(
                    horizontal: 12,
                    vertical: 8,
                  ),
                ),
              ),
            ],
          ),
        ),
        Expanded(
          child: ListView(
            padding: EdgeInsets.zero,
            children: stageData['suggestions']!,
          ),
        ),
      ],
    );
  }

  Map<String, dynamic> _getStageData(int stage) {
    switch (stage) {
      case 1:
        return {
          'title': 'Soil Preparation',
          'suggestions': [
            SuggestionCard(
              suggestion: Suggestion(
                title: 'Plowing Depth',
                description:
                    'AI Suggestion: Deep plowing (15-20 cm) is recommended for your clay loam soil to improve aeration and root penetration. Current soil moisture at 18% is optimal for plowing.',
                icon: Icons.layers,
                iconColor: Colors.brown,
                actions: [
                  ElevatedButton(
                    onPressed: () {},
                    child: const Text('Watch Tutorial'),
                  ),
                  OutlinedButton(
                    onPressed: () {},
                    child: const Text('Read Guide'),
                  ),
                ],
              ),
            ),
          ],
        };
      case 2:
        return {
          'title': 'Seed Sowing',
          'suggestions': [
            SuggestionCard(
              suggestion: Suggestion(
                title: 'Sowing Time',
                description:
                    'Weather forecast predicts a light shower in 2 days. It is ideal to sow your wheat seeds tomorrow.',
                icon: Icons.cloudy_snowing,
                iconColor: Colors.lightBlue,
              ),
            ),
            SuggestionCard(
              suggestion: Suggestion(
                title: 'Seed Treatment',
                description:
                    'To prevent fungal diseases, treat seeds with recommended fungicides before sowing.',
                icon: Icons.science,
                iconColor: Colors.purple,
                actions: [
                  OutlinedButton(
                    onPressed: () {},
                    child: const Text('View Fungicides'),
                  ),
                ],
              ),
            ),
          ],
        };
      case 3:
        return {
          'title': 'Crop Growth',
          'suggestions': [
            SuggestionCard(
              suggestion: Suggestion(
                title: 'Irrigation',
                description:
                    'Next 3 days are expected to be dry and sunny. Irrigate the field lightly to maintain soil moisture.',
                icon: Icons.water_drop,
                iconColor: Colors.blue,
                actions: [
                  ElevatedButton(
                    onPressed: () {},
                    child: const Text('Check Weather'),
                  ),
                ],
              ),
            ),
            SuggestionCard(
              suggestion: Suggestion(
                title: 'Nutrient Management',
                description:
                    'Your crop is at the tillering stage. A dose of Nitrogen is recommended. Apply 50kg/ha of Urea.',
                icon: Icons.eco,
                iconColor: Colors.green,
              ),
            ),
          ],
        };
      case 4:
        return {
          'title': 'Harvesting',
          'suggestions': [
            SuggestionCard(
              suggestion: Suggestion(
                title: 'Harvesting Time',
                description:
                    'The crop has reached physiological maturity. Grains are hard and contain around 20% moisture. Ideal time to harvest is within the next 2-3 days.',
                icon: Icons.cut,
                iconColor: Colors.orange,
              ),
            ),
          ],
        };
      case 5:
        return {
          'title': 'Post-Harvest',
          'suggestions': [
            SuggestionCard(
              suggestion: Suggestion(
                title: 'Storage',
                description:
                    'Dry the grains to 12% moisture before storing to prevent pest infestation and mold.',
                icon: Icons.inventory,
                iconColor: Colors.brown.shade700,
              ),
            ),
            SuggestionCard(
              suggestion: Suggestion(
                title: 'Market Prices',
                description:
                    'Current market price for wheat in your local Mandi is ₹2,100/quintal. Prices are expected to rise next week.',
                icon: Icons.trending_up,
                iconColor: Colors.green,
                actions: [
                  ElevatedButton(
                    onPressed: () {},
                    child: const Text('View Mandi Prices'),
                  ),
                ],
              ),
            ),
          ],
        };
      default:
        return {'title': 'Unknown Stage', 'suggestions': []};
    }
  }
}
