import 'package:flutter/material.dart';
import 'package:youtube_player_flutter/youtube_player_flutter.dart';
import '../models/video_recommendation.dart';
import '../services/youtube_api_service.dart';
import '../services/firebase_service.dart';

class VideoCarousel extends StatefulWidget {
  const VideoCarousel({super.key});

  @override
  State<VideoCarousel> createState() => _VideoCarouselState();
}

class _VideoCarouselState extends State<VideoCarousel> {
  late PageController _pageController;
  List<VideoRecommendation> _recommendations = [];
  bool _isLoading = true;
  bool _isShowingFallbackVideos = false;

  @override
  void initState() {
    super.initState();
    _pageController = PageController(viewportFraction: 0.85);
    _loadRecommendations();
  }

  Future<void> _loadRecommendations() async {
    try {
      setState(() {
        _isLoading = true;
        _isShowingFallbackVideos = false;
      });

      final String? farmerId = FirebaseService.getCurrentUserId();
      if (farmerId != null) {
        final recommendations = await YouTubeApiService.getVideoRecommendations(
          farmerId,
        );

        if (recommendations.isNotEmpty) {
          setState(() {
            _recommendations = recommendations;
            _isLoading = false;
            _isShowingFallbackVideos = false;
          });
          return;
        }
      }

      // Fallback 1: Try keyword search with agricultural terms
      final fallbackVideos = await YouTubeApiService.searchVideosByKeywords([
        'organic farming techniques',
        'crop disease management',
        'modern agriculture methods',
        'sustainable farming practices',
        'किसान खेती तकनीक',
      ], maxResults: 5);

      if (fallbackVideos.isNotEmpty) {
        setState(() {
          _recommendations = fallbackVideos;
          _isLoading = false;
          _isShowingFallbackVideos = true;
        });
        return;
      }

      // Fallback 2: Use curated educational videos
      setState(() {
        _recommendations = YouTubeApiService.getEducationalFallbackVideos();
        _isLoading = false;
        _isShowingFallbackVideos = true;
      });
    } catch (e) {
      print('Error loading recommendations: $e');
      // Final fallback: Use educational videos
      setState(() {
        _recommendations = YouTubeApiService.getEducationalFallbackVideos();
        _isLoading = false;
        _isShowingFallbackVideos = true;
      });
    }
  }

  @override
  void dispose() {
    _pageController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        // Header with refresh button for fallback videos
        if (_isShowingFallbackVideos && !_isLoading)
          Container(
            padding: const EdgeInsets.only(bottom: 8.0),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  'सामान्य वीडियो दिखाए जा रहे हैं',
                  style: TextStyle(
                    color: Color(0xFF708A58),
                    fontSize: 12,
                    fontStyle: FontStyle.italic,
                  ),
                ),
                Container(
                  decoration: BoxDecoration(
                    color: Color(0xFF2D4F2B),
                    borderRadius: BorderRadius.circular(6),
                  ),
                  child: IconButton(
                    onPressed: _loadRecommendations,
                    icon: Icon(Icons.refresh, color: Colors.white, size: 18),
                    constraints: BoxConstraints(minWidth: 32, minHeight: 32),
                    padding: EdgeInsets.all(6),
                    tooltip: 'व्यक्तिगत वीडियो के लिए पुनः प्रयास करें',
                  ),
                ),
              ],
            ),
          ),
        // Video carousel content
        _buildVideoCarouselContent(),
      ],
    );
  }

  Widget _buildVideoCarouselContent() {
    if (_isLoading) {
      return Container(
        height: 250,
        child: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              CircularProgressIndicator(
                color: Color(0xFF2D4F2B),
                strokeWidth: 3,
              ),
              SizedBox(height: 16),
              Text(
                'किसान के लिए वीडियो लोड हो रहे हैं...',
                style: TextStyle(color: Color(0xFF708A58), fontSize: 14),
              ),
            ],
          ),
        ),
      );
    }

    if (_recommendations.isEmpty) {
      return Container(
        height: 250,
        child: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(
                Icons.video_library_outlined,
                color: Color(0xFF708A58),
                size: 48,
              ),
              SizedBox(height: 8),
              Text(
                'कोई वीडियो उपलब्ध नहीं है',
                style: TextStyle(color: Color(0xFF708A58), fontSize: 16),
              ),
              SizedBox(height: 8),
              ElevatedButton(
                onPressed: _loadRecommendations,
                style: ElevatedButton.styleFrom(
                  backgroundColor: Color(0xFF2D4F2B),
                ),
                child: Text(
                  'फिर से कोशिश करें',
                  style: TextStyle(color: Colors.white),
                ),
              ),
            ],
          ),
        ),
      );
    }

    return SizedBox(
      height: 250,
      child: PageView.builder(
        padEnds: false,
        controller: _pageController,
        itemCount: _recommendations.length,
        itemBuilder: (context, index) {
          final video = _recommendations[index];
          final videoId = video.videoId;

          if (videoId == null) {
            return Card(
              margin: const EdgeInsets.symmetric(horizontal: 8.0),
              elevation: 4,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12),
              ),
              child: Center(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Icon(Icons.error_outline, color: Colors.red, size: 32),
                    SizedBox(height: 8),
                    Text(
                      'वीडियो लोड नहीं हो सका',
                      style: TextStyle(fontSize: 12),
                    ),
                  ],
                ),
              ),
            );
          }

          return Card(
            margin: const EdgeInsets.symmetric(horizontal: 8.0),
            elevation: 4,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(12),
            ),
            child: ClipRRect(
              borderRadius: BorderRadius.circular(12),
              child: Column(
                children: [
                  Expanded(
                    flex: 5,
                    child: YoutubePlayer(
                      controller: YoutubePlayerController(
                        initialVideoId: videoId,
                        flags: const YoutubePlayerFlags(
                          autoPlay: false,
                          mute: false,
                          enableCaption: true,
                          forceHD: false,
                        ),
                      ),
                      showVideoProgressIndicator: true,
                      progressIndicatorColor: Color(0xFF2D4F2B),
                      bottomActions: [
                        CurrentPosition(),
                        ProgressBar(
                          isExpanded: true,
                          colors: ProgressBarColors(
                            playedColor: Color(0xFF2D4F2B),
                            handleColor: Color(0xFFFFB823),
                          ),
                        ),
                        RemainingDuration(),
                      ],
                    ),
                  ),
                  Expanded(
                    flex: 2,
                    child: Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 12.0,
                        vertical: 8.0,
                      ),
                      width: double.infinity,
                      color: Colors.white,
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        mainAxisAlignment: MainAxisAlignment.start,
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Flexible(
                            child: Text(
                              video.title,
                              style: TextStyle(
                                fontWeight: FontWeight.w600,
                                fontSize: 11,
                                color: Color(0xFF2D4F2B),
                                height: 1.1,
                              ),
                              maxLines: 2,
                              overflow: TextOverflow.ellipsis,
                            ),
                          ),
                          if (video.channel != null) ...[
                            SizedBox(height: 4),
                            Flexible(
                              child: Row(
                                children: [
                                  Icon(
                                    Icons.account_circle,
                                    size: 12,
                                    color: Color(0xFF708A58),
                                  ),
                                  SizedBox(width: 4),
                                  Expanded(
                                    child: Text(
                                      video.channel!,
                                      style: TextStyle(
                                        color: Color(0xFF708A58),
                                        fontSize: 9,
                                        fontWeight: FontWeight.w500,
                                      ),
                                      overflow: TextOverflow.ellipsis,
                                    ),
                                  ),
                                  if (video.duration != null) ...[
                                    SizedBox(width: 4),
                                    Icon(
                                      Icons.access_time,
                                      size: 10,
                                      color: Color(0xFF708A58),
                                    ),
                                    SizedBox(width: 2),
                                    Text(
                                      video.duration!,
                                      style: TextStyle(
                                        color: Color(0xFF708A58),
                                        fontSize: 9,
                                        fontWeight: FontWeight.w500,
                                      ),
                                    ),
                                  ],
                                ],
                              ),
                            ),
                          ],
                        ],
                      ),
                    ),
                  ),
                ],
              ),
            ),
          );
        },
      ),
    );
  }
}
