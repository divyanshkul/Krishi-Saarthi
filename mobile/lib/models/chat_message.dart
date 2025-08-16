import 'chat_response_model.dart';

class ChatMessage {
  final bool isUser;
  final String text;
  final ChatResponseModel? aiResponse;
  final DateTime timestamp;

  const ChatMessage({
    required this.isUser,
    required this.text,
    this.aiResponse,
    required this.timestamp,
  });

  factory ChatMessage.user(String text) {
    return ChatMessage(
      isUser: true,
      text: text,
      timestamp: DateTime.now(),
    );
  }

  factory ChatMessage.ai(ChatResponseModel response) {
    return ChatMessage(
      isUser: false,
      text: response.text,
      aiResponse: response,
      timestamp: DateTime.now(),
    );
  }
}