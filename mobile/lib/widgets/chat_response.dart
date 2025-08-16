import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';
import 'video_player_modal.dart';

class ChatResponseCard extends StatelessWidget {
  final bool isUser;
  final String text;
  final String? videoUrl;
  final String? videoTitle;
  final String? websiteUrl;
  final String? websiteTitle;

  const ChatResponseCard({
    super.key,
    this.isUser = false,
    required this.text,
    this.videoUrl,
    this.videoTitle,
    this.websiteUrl,
    this.websiteTitle,
  });

  @override
  Widget build(BuildContext context) {
    if (isUser) {
      return _buildUserMessage();
    }
    return _buildAIMessage(context);
  }

  Widget _buildUserMessage() {
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

  Widget _buildAIMessage(BuildContext context) {
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
            if (_hasActions) ...[
              const SizedBox(height: 12),
              Wrap(
                spacing: 8,
                runSpacing: 8,
                children: [
                  if (_hasVideo) _buildVideoButton(context),
                  if (_hasWebsite) _buildWebsiteButton(),
                ],
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildVideoButton(BuildContext context) {
    return Container(
      constraints: const BoxConstraints(minWidth: 140, maxWidth: 200),
      child: ElevatedButton.icon(
        onPressed: () => _onVideoTap(context),
        icon: const Icon(Icons.play_circle, size: 18),
        label: Text(
          videoTitle ?? 'Watch Video',
          style: const TextStyle(fontSize: 13),
          overflow: TextOverflow.ellipsis,
        ),
        style: ElevatedButton.styleFrom(
          backgroundColor: Colors.green.shade700,
          foregroundColor: Colors.white,
          elevation: 2,
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
          minimumSize: const Size(0, 36),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(20),
          ),
        ),
      ),
    );
  }

  Widget _buildWebsiteButton() {
    return Container(
      constraints: const BoxConstraints(minWidth: 140, maxWidth: 200),
      child: OutlinedButton.icon(
        onPressed: _onWebsiteTap,
        icon: const Icon(Icons.language, size: 18),
        label: Text(
          websiteTitle ?? 'View Website',
          style: const TextStyle(fontSize: 13),
          overflow: TextOverflow.ellipsis,
        ),
        style: OutlinedButton.styleFrom(
          side: BorderSide(color: Colors.green.shade700, width: 1.5),
          foregroundColor: Colors.green.shade700,
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
          minimumSize: const Size(0, 36),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(20),
          ),
        ),
      ),
    );
  }

  bool get _hasVideo => videoUrl != null && videoUrl!.isNotEmpty;
  bool get _hasWebsite => websiteUrl != null && websiteUrl!.isNotEmpty;
  bool get _hasActions => _hasVideo || _hasWebsite;

  void _onVideoTap(BuildContext context) {
    if (_hasVideo) {
      VideoPlayerModal.show(context, videoUrl!, videoTitle);
    }
  }

  void _onWebsiteTap() async {
    if (_hasWebsite) {
      final uri = Uri.parse(websiteUrl!);
      if (await canLaunchUrl(uri)) {
        await launchUrl(uri, mode: LaunchMode.externalApplication);
      }
    }
  }
}
