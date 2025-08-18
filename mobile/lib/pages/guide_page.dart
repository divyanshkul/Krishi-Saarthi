import 'package:flutter/material.dart';
import '../models/suggestion.dart';
import '../models/guided_mode.dart';
import '../widgets/app_header.dart';
import '../widgets/stage_progress_bar.dart';
import '../widgets/suggestion_card.dart';
import '../widgets/video_player_modal.dart';
import '../services/guided_mode_service.dart';
import '../services/firebase_service.dart';
import 'package:url_launcher/url_launcher.dart';

class GuidePage extends StatefulWidget {
  const GuidePage({super.key});

  @override
  State<GuidePage> createState() => _GuidePageState();
}

class _GuidePageState extends State<GuidePage> {
  int _currentStage = 1;
  bool _isLoading = false;
  GuidedModeResponse? _guidanceData;
  String? _error;
  final GuidedModeService _guidedModeService = GuidedModeService();

  @override
  void initState() {
    super.initState();
    _loadGuidanceData();
  }

  void _onStageSelected(int stage) {
    setState(() {
      _currentStage = stage;
    });
  }

  Future<void> _loadGuidanceData() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      // Get farmer's primary crop from Firebase
      final userCrops = await FirebaseService.getUserCrops();
      String cropName = 'wheat'; // Default crop
      String? farmerId = FirebaseService.getCurrentUserId();

      if (userCrops.isNotEmpty) {
        cropName = userCrops.first.cropType.toLowerCase();
      }

      final response = await _guidedModeService.getCropGuidance(
        cropName,
        farmerId: farmerId,
      );

      if (response != null && response.success) {
        setState(() {
          _guidanceData = response;
          _isLoading = false;
        });
      } else {
        // Use fallback guidance if API fails
        setState(() {
          _guidanceData = GuidedModeService.getFallbackGuidance(cropName);
          _isLoading = false;
        });
      }
    } catch (e) {
      // Use fallback guidance if error occurs
      setState(() {
        _guidanceData = GuidedModeService.getFallbackGuidance('wheat');
        _error = null; // Don't show error, just use fallback
        _isLoading = false;
      });
    }
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
              child: _buildContent(),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildContent() {
    if (_isLoading) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            CircularProgressIndicator(color: Colors.green),
            SizedBox(height: 16),
            Text(
              'Loading AI guidance...',
              style: TextStyle(color: Colors.green.shade700, fontSize: 16),
            ),
          ],
        ),
      );
    }

    if (_error != null) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.error_outline, size: 64, color: Colors.red),
            SizedBox(height: 16),
            Text(_error!, style: TextStyle(color: Colors.red)),
            SizedBox(height: 16),
            ElevatedButton(onPressed: _loadGuidanceData, child: Text('Retry')),
          ],
        ),
      );
    }

    if (_guidanceData == null) {
      return _buildStageContent(_currentStage); // Fallback to static content
    }

    return _buildAIStageContent(_currentStage);
  }

  Widget _buildAIStageContent(int stage) {
    final stageData = _guidanceData!.getStageByNumber(stage);

    if (stageData == null) {
      return _buildStageContent(stage); // Fallback to static content
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.symmetric(vertical: 8.0),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Expanded(
                child: Text(
                  stageData.stageName,
                  style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
              Container(
                padding: EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                decoration: BoxDecoration(
                  color: Colors.green.shade100,
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(
                      Icons.auto_awesome,
                      size: 16,
                      color: Colors.green.shade700,
                    ),
                    SizedBox(width: 4),
                    Text(
                      'AI Powered',
                      style: TextStyle(
                        color: Colors.green.shade700,
                        fontSize: 12,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
        Expanded(
          child: ListView.builder(
            padding: EdgeInsets.zero,
            itemCount: stageData.topics.length,
            itemBuilder: (context, index) {
              final topic = stageData.topics[index];
              return _buildAITopicCard(topic);
            },
          ),
        ),
      ],
    );
  }

  Widget _buildAITopicCard(GuidanceTopic topic) {
    List<Widget> actions = [];

    // Add video buttons
    for (int i = 0; i < topic.videoLinks.length; i++) {
      actions.add(
        ElevatedButton.icon(
          onPressed: () => _openVideo(topic.videoLinks[i]),
          icon: Icon(Icons.play_circle, size: 18),
          label: Text('Watch Tutorial ${i + 1}'),
          style: ElevatedButton.styleFrom(
            backgroundColor: Colors.green.shade700,
            foregroundColor: Colors.white,
          ),
        ),
      );
    }

    // Add article buttons
    for (int i = 0; i < topic.articles.length; i++) {
      actions.add(
        OutlinedButton.icon(
          onPressed: () => _openArticle(topic.articles[i]),
          icon: Icon(Icons.article, size: 18),
          label: Text('Read Article ${i + 1}'),
          style: OutlinedButton.styleFrom(
            foregroundColor: Colors.green.shade700,
          ),
        ),
      );
    }

    return SuggestionCard(
      suggestion: Suggestion(
        title: topic.title,
        description: topic.description,
        icon: topic.iconData,
        iconColor: Colors.green.shade700,
        actions: actions.isNotEmpty ? actions : null,
      ),
    );
  }

  void _openVideo(String videoUrl) {
    if (videoUrl.isNotEmpty) {
      VideoPlayerModal.show(context, videoUrl, null);
    }
  }

  void _openArticle(String articleUrl) async {
    if (articleUrl.isNotEmpty) {
      final uri = Uri.parse(articleUrl);
      if (await canLaunchUrl(uri)) {
        await launchUrl(uri, mode: LaunchMode.externalApplication);
      }
    }
  }

  // Fallback static content (existing implementation)
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
              Expanded(
                child: Text(
                  stageData['title']!,
                  style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
              ElevatedButton.icon(
                onPressed: _loadGuidanceData,
                icon: const Icon(Icons.refresh, size: 18),
                label: const Text('Load AI'),
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
