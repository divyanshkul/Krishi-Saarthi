import 'package:flutter/material.dart';
import '../widgets/app_header.dart';
import '../widgets/chat_response.dart';

class ChatPage extends StatelessWidget {
  const ChatPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Column(
        children: [
          const AppHeader(),
          Expanded(
            child: ListView(
              padding: const EdgeInsets.all(12),
              children: [
                const ChatResponseCard(
                  isUser: false,
                  text: 'Hello! I am your Krishi Saarthi.',
                  aiTitle: null,
                ),
                const ChatResponseCard(
                  isUser: true,
                  text: 'I am seeing yellow leaves in my wheat crop',
                ),
                const ChatResponseCard(
                  isUser: false,
                  text:
                      'Yellow leaves can be due to nitrogen deficiency. I am looking for a solution for you...',
                  aiTitle: 'AI Analysis (95% confidence):',
                  aiBullets: [
                    'Urea: 10 kg/acre',
                    'Spray with water',
                    'Improvement will be visible in 7 days',
                  ],
                  showActions: true,
                ),
              ],
            ),
          ),
          _buildInputBar(),
        ],
      ),
    );
  }
  // Weather is shown in the shared AppHeader; detailed suggestion is now a ChatResponseCard.

  Widget _buildInputBar() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      decoration: BoxDecoration(
        color: Colors.white,
        boxShadow: [BoxShadow(color: Colors.black12, blurRadius: 6)],
      ),
      child: Row(
        children: [
          IconButton(onPressed: () {}, icon: const Icon(Icons.camera_alt)),
          Expanded(
            child: TextField(
              decoration: InputDecoration(
                hintText: 'Ask your question...',
                border: InputBorder.none,
              ),
            ),
          ),
          const SizedBox(width: 8),
          CircleAvatar(
            backgroundColor: Colors.green,
            child: const Icon(Icons.send, color: Colors.white),
          ),
          IconButton(
            onPressed: () {},
            icon: const Icon(Icons.mic),
            color: Colors.green,
          ),
        ],
      ),
    );
  }
}
