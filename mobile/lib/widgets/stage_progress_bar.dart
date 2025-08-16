import 'package:flutter/material.dart';

class StageProgressBar extends StatelessWidget {
  final int currentStage;
  final Function(int) onStageSelected;

  const StageProgressBar({
    super.key,
    required this.currentStage,
    required this.onStageSelected,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 24.0, vertical: 8.0),
          child: LinearProgressIndicator(
            value: currentStage / 5.0,
            backgroundColor: Colors.grey.shade300,
            valueColor: const AlwaysStoppedAnimation<Color>(Colors.green),
            minHeight: 6,
          ),
        ),
        const SizedBox(height: 8),
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceAround,
          children: List.generate(5, (index) {
            return _buildStageIcon(index + 1);
          }),
        ),
      ],
    );
  }

  Widget _buildStageIcon(int stage) {
    final bool isSelected = currentStage == stage;
    final stageData = _getStageData(stage);

    return GestureDetector(
      onTap: () => onStageSelected(stage),
      child: Column(
        children: [
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              color: isSelected ? Colors.green.shade100 : Colors.grey.shade200,
              border: Border.all(
                color: isSelected ? Colors.green : Colors.transparent,
                width: 2,
              ),
              boxShadow: isSelected
                  ? [
                      BoxShadow(
                        color: Colors.green.withOpacity(0.5),
                        blurRadius: 10,
                        spreadRadius: 2,
                      ),
                    ]
                  : [],
            ),
            child: Icon(
              stageData['icon'],
              color: isSelected ? Colors.green.shade800 : Colors.grey.shade600,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            stageData['label']!,
            style: TextStyle(
              fontSize: 12,
              fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
              color: isSelected ? Colors.green.shade800 : Colors.grey.shade700,
            ),
          ),
        ],
      ),
    );
  }

  Map<String, dynamic> _getStageData(int stage) {
    switch (stage) {
      case 1:
        return {'icon': Icons.eco, 'label': 'Soil Prep'};
      case 2:
        return {'icon': Icons.grain, 'label': 'Sowing'};
      case 3:
        return {'icon': Icons.grass, 'label': 'Growth'};
      case 4:
        return {'icon': Icons.agriculture, 'label': 'Harvest'};
      case 5:
        return {'icon': Icons.inventory_2, 'label': 'Post-Harvest'};
      default:
        return {'icon': Icons.help, 'label': 'Unknown'};
    }
  }
}
