import 'package:flutter/material.dart';

class ChatResponseCard extends StatelessWidget {
  final bool isUser;
  final String text;
  final String? aiTitle;
  final List<String>? aiBullets;
  final bool showActions;

  const ChatResponseCard({
    super.key,
    this.isUser = false,
    required this.text,
    this.aiTitle,
    this.aiBullets,
    this.showActions = false,
  });

  @override
  Widget build(BuildContext context) {
    if (isUser) {
      return Align(
        alignment: Alignment.centerRight,
        child: Container(
          margin: const EdgeInsets.symmetric(vertical: 6),
          padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
          decoration: BoxDecoration(
            color: Colors.green.shade700,
            borderRadius: BorderRadius.circular(20),
          ),
          child: Text(text, style: const TextStyle(color: Colors.white)),
        ),
      );
    }

    // AI response card
    return Align(
      alignment: Alignment.centerLeft,
      child: Container(
        width: MediaQuery.of(context).size.width * 0.75,
        margin: const EdgeInsets.symmetric(vertical: 6),
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(12),
          boxShadow: [BoxShadow(color: Colors.black12, blurRadius: 6)],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(text),
            if (aiTitle != null ||
                (aiBullets != null && aiBullets!.isNotEmpty)) ...[
              const SizedBox(height: 8),
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(
                  color: Colors.green.shade50,
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    if (aiTitle != null)
                      Text(
                        aiTitle!,
                        style: const TextStyle(fontWeight: FontWeight.bold),
                      ),
                    if (aiBullets != null)
                      ...aiBullets!.map(
                        (b) => Padding(
                          padding: const EdgeInsets.only(top: 6),
                          child: Text(b),
                        ),
                      ),
                  ],
                ),
              ),
            ],
            if (showActions) ...[
              const SizedBox(height: 8),
              Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  ElevatedButton.icon(
                    onPressed: () {},
                    icon: const Icon(Icons.play_circle),
                    label: const Text('Watch Video'),
                  ),
                  const SizedBox(height: 8),
                  OutlinedButton.icon(
                    onPressed: () {},
                    icon: const Icon(Icons.phone),
                    label: const Text('Call Expert'),
                  ),
                ],
              ),
            ],
          ],
        ),
      ),
    );
  }
}
