import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:krishi_saarthi_mobile/screens/voice_recording_screen.dart';
import '../widgets/app_header.dart';
import '../widgets/chat_response.dart';
import '../providers/recording_provider.dart';

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
          Consumer<RecordingProvider>(
            builder: (context, recordingProvider, child) {
              return Column(
                children: [
                  if (recordingProvider.hasRecording) _buildRecordingAttachment(context, recordingProvider),
                  _buildInputBar(context),
                ],
              );
            },
          ),
        ],
      ),
    );
  }
  // Weather is shown in the shared AppHeader; detailed suggestion is now a ChatResponseCard.

  Widget _buildRecordingAttachment(BuildContext context, RecordingProvider recordingProvider) {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      decoration: BoxDecoration(
        color: Colors.green.shade50,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.green.shade200),
      ),
      child: Row(
        children: [
          Icon(Icons.audiotrack, color: Colors.green.shade600, size: 20),
          const SizedBox(width: 8),
          Expanded(
            child: Text(
              recordingProvider.getRecordingDisplayName() ?? 'Audio recording',
              style: TextStyle(
                color: Colors.green.shade700,
                fontSize: 14,
                fontWeight: FontWeight.w500,
              ),
            ),
          ),
          GestureDetector(
            onTap: () => recordingProvider.clearRecording(),
            child: Icon(
              Icons.close,
              color: Colors.green.shade600,
              size: 18,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildInputBar(BuildContext context) {
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
          Consumer<RecordingProvider>(
            builder: (context, recordingProvider, child) {
              return IconButton(
                onPressed: () {
                  Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (context) => const VoiceRecordingScreen(),
                    ),
                  );
                },
                icon: const Icon(Icons.mic),
                color: recordingProvider.hasRecording ? Colors.green.shade700 : Colors.green,
              );
            },
          ),
          Consumer<RecordingProvider>(
            builder: (context, recordingProvider, child) {
              return GestureDetector(
                onTap: () => _handleSend(context, recordingProvider),
                child: CircleAvatar(
                  backgroundColor: recordingProvider.isProcessing 
                      ? Colors.grey 
                      : Colors.green,
                  child: recordingProvider.isProcessing
                      ? SizedBox(
                          width: 20,
                          height: 20,
                          child: CircularProgressIndicator(
                            color: Colors.white,
                            strokeWidth: 2,
                          ),
                        )
                      : const Icon(Icons.send, color: Colors.white),
                ),
              );
            },
          ),
        ],
      ),
    );
  }

  void _handleSend(BuildContext context, RecordingProvider recordingProvider) async {
    // Prevent sending if already processing
    if (recordingProvider.isProcessing) return;

    // Check if there's a recording to process
    if (recordingProvider.hasRecording) {
      // Process audio recording
      await recordingProvider.processAudio();
      
      // Handle the result
      if (recordingProvider.processingState == ProcessingState.success) {
        // Add AI response to chat (we'll implement this next)
        debugPrint('AI Response: ${recordingProvider.aiResponse}');
      } else if (recordingProvider.processingState == ProcessingState.error) {
        // Show error message
        if (context.mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text('Error: ${recordingProvider.processingError}'),
              backgroundColor: Colors.red,
            ),
          );
        }
      }
    } else {
      // Handle text input (to be implemented later)
      debugPrint('No recording or text to send');
    }
  }
}
