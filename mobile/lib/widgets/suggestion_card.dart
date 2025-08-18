import 'package:flutter/material.dart';
import '../models/suggestion.dart';

class SuggestionCard extends StatelessWidget {
  final Suggestion suggestion;

  const SuggestionCard({super.key, required this.suggestion});

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      margin: const EdgeInsets.symmetric(vertical: 8),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(suggestion.icon, color: suggestion.iconColor),
                const SizedBox(width: 8),
                Text(
                  suggestion.title,
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Text(suggestion.description),
            if (suggestion.actions != null &&
                suggestion.actions!.isNotEmpty) ...[
              const SizedBox(height: 16),
              Wrap(spacing: 8, runSpacing: 8, children: suggestion.actions!),
            ],
          ],
        ),
      ),
    );
  }
}
