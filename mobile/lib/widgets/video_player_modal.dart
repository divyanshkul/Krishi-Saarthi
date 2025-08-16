import 'package:flutter/material.dart';
import 'package:youtube_player_flutter/youtube_player_flutter.dart';

class VideoPlayerModal extends StatefulWidget {
  final String videoUrl;
  final String? title;

  const VideoPlayerModal({
    super.key,
    required this.videoUrl,
    this.title,
  });

  static void show(BuildContext context, String videoUrl, String? title) {
    showDialog(
      context: context,
      barrierDismissible: true,
      builder: (context) => VideoPlayerModal(
        videoUrl: videoUrl,
        title: title,
      ),
    );
  }

  @override
  State<VideoPlayerModal> createState() => _VideoPlayerModalState();
}

class _VideoPlayerModalState extends State<VideoPlayerModal> {
  late YoutubePlayerController _controller;
  String? videoId;

  @override
  void initState() {
    super.initState();
    videoId = YoutubePlayer.convertUrlToId(widget.videoUrl);
    if (videoId != null) {
      _controller = YoutubePlayerController(
        initialVideoId: videoId!,
        flags: const YoutubePlayerFlags(
          autoPlay: false,
          mute: false,
        ),
      );
    }
  }

  @override
  void dispose() {
    if (videoId != null) {
      _controller.dispose();
    }
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    if (videoId == null) {
      return Dialog(
        child: Container(
          padding: const EdgeInsets.all(20),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Icon(Icons.error, size: 48, color: Colors.red),
              const SizedBox(height: 16),
              const Text(
                'Invalid video URL',
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 8),
              const Text('Unable to load the video. Please try again later.'),
              const SizedBox(height: 16),
              ElevatedButton(
                onPressed: () => Navigator.of(context).pop(),
                child: const Text('Close'),
              ),
            ],
          ),
        ),
      );
    }

    return Dialog(
      insetPadding: const EdgeInsets.all(16),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          AppBar(
            title: Text(
              widget.title ?? 'Educational Video',
              style: const TextStyle(fontSize: 16),
            ),
            leading: IconButton(
              icon: const Icon(Icons.close),
              onPressed: () => Navigator.of(context).pop(),
            ),
            backgroundColor: Colors.green.shade700,
            foregroundColor: Colors.white,
          ),
          Container(
            constraints: BoxConstraints(
              maxHeight: MediaQuery.of(context).size.height * 0.7,
            ),
            child: YoutubePlayer(
              controller: _controller,
              showVideoProgressIndicator: true,
              aspectRatio: 16 / 9,
            ),
          ),
        ],
      ),
    );
  }
}