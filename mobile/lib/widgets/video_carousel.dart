import 'package:flutter/material.dart';
import 'package:youtube_player_flutter/youtube_player_flutter.dart';

class VideoCarousel extends StatefulWidget {
  const VideoCarousel({super.key});

  @override
  State<VideoCarousel> createState() => _VideoCarouselState();
}

class _VideoCarouselState extends State<VideoCarousel> {
  final List<String> _videoIds = [
    'dQw4w9WgXcQ',
    'L_LUpnjgPso',
    'dQw4w9WgXcQ',
    // Add more video IDs here
  ];

  late PageController _pageController;

  @override
  void initState() {
    super.initState();
    _pageController = PageController(viewportFraction: 0.85);
  }

  @override
  void dispose() {
    _pageController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      height: 200,
      child: PageView.builder(
        padEnds: false,
        controller: _pageController,
        itemCount: _videoIds.length,
        itemBuilder: (context, index) {
          return Card(
            margin: const EdgeInsets.symmetric(horizontal: 8.0),
            child: YoutubePlayer(
              controller: YoutubePlayerController(
                initialVideoId: _videoIds[index],
                flags: const YoutubePlayerFlags(autoPlay: false, mute: false),
              ),
              showVideoProgressIndicator: true,
            ),
          );
        },
      ),
    );
  }
}
