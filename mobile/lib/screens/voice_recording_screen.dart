import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../widgets/particle_animation_widget.dart';
import '../services/audio_recording_service.dart';
import '../providers/recording_provider.dart';

class VoiceRecordingScreen extends StatefulWidget {
  const VoiceRecordingScreen({super.key});

  @override
  State<VoiceRecordingScreen> createState() => _VoiceRecordingScreenState();
}

class _VoiceRecordingScreenState extends State<VoiceRecordingScreen> {
  final AudioRecordingService _audioService = AudioRecordingService();
  bool _isRecording = false;
  String _statusText = "Say something...";

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey.shade100,
      body: SafeArea(
        child: Stack(
          children: [
            // Close button
            Positioned(
              top: 20,
              left: 20,
              child: GestureDetector(
                onTap: () => Navigator.pop(context),
                child: Container(
                  width: 40,
                  height: 40,
                  decoration: const BoxDecoration(
                    color: Colors.black12,
                    shape: BoxShape.circle,
                  ),
                  child: const Icon(
                    Icons.close,
                    color: Colors.black54,
                    size: 20,
                  ),
                ),
              ),
            ),

            // Main content
            Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  // Particle animation area
                  SizedBox(
                    width: 320,
                    height: 320,
                    child: Stack(
                      alignment: Alignment.center,
                      children: [
                        // Particle animation
                        const ParticleAnimationWidget(
                          radius: 150,
                          particleCount: 350,
                        ),
                      ],
                    ),
                  ),

                  const SizedBox(height: 60),

                  // Recording controls
                  Column(
                    children: [
                      // Status text above button
                      if (!_isRecording)
                        Text(
                          _statusText,
                          style: const TextStyle(
                            fontSize: 18,
                            color: Colors.black54,
                            fontWeight: FontWeight.w500,
                          ),
                          textAlign: TextAlign.center,
                        ),

                      const SizedBox(height: 16),

                      // Microphone button
                      GestureDetector(
                        onTap: _toggleRecording,
                        child: Container(
                          width: 64,
                          height: 64,
                          decoration: BoxDecoration(
                            color: _isRecording
                                ? Colors.red.shade400
                                : Colors.grey.shade300,
                            shape: BoxShape.circle,
                            boxShadow: [
                              BoxShadow(
                                color: Colors.black.withValues(alpha: 0.1),
                                blurRadius: 8,
                                offset: const Offset(0, 2),
                              ),
                            ],
                          ),
                          child: Icon(
                            _isRecording ? Icons.stop : Icons.mic,
                            color: _isRecording ? Colors.white : Colors.black54,
                            size: 28,
                          ),
                        ),
                      ),
                    ],
                  ),

                  const SizedBox(height: 20),

                  // Recording status
                  if (_isRecording)
                    Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Container(
                          width: 8,
                          height: 8,
                          decoration: const BoxDecoration(
                            color: Colors.red,
                            shape: BoxShape.circle,
                          ),
                        ),
                        const SizedBox(width: 8),
                        const Text(
                          "Recording...",
                          style: TextStyle(
                            fontSize: 16,
                            color: Colors.red,
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                      ],
                    ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }


  Future<void> _toggleRecording() async {
    if (_isRecording) {
      // Stop recording
      final String? savedPath = await _audioService.stopRecording();

      if (savedPath != null) {
        // Save recording to provider
        if (mounted) {
          context.read<RecordingProvider>().setRecording(savedPath);
        }
        
        setState(() {
          _isRecording = false;
          _statusText = "Recording saved!";
        });

        // Auto-navigate back after brief success message
        Future.delayed(const Duration(seconds: 1), () {
          if (mounted) {
            Navigator.pop(context);
          }
        });
      } else {
        setState(() {
          _isRecording = false;
          _statusText = "Failed to save recording";
        });

        // Reset status text after 3 seconds
        Future.delayed(const Duration(seconds: 3), () {
          if (mounted) {
            setState(() {
              _statusText = "Say something...";
            });
          }
        });
      }
    } else {
      // Start recording
      final bool started = await _audioService.startRecording();

      if (started) {
        setState(() {
          _isRecording = true;
          _statusText = "";
        });
      } else {
        setState(() {
          _statusText = "Permission denied or error starting recording";
        });

        // Reset status text after 3 seconds
        Future.delayed(const Duration(seconds: 3), () {
          if (mounted) {
            setState(() {
              _statusText = "Say something...";
            });
          }
        });
      }
    }
  }

  @override
  void dispose() {
    // Cancel any ongoing recording when leaving the screen
    if (_isRecording) {
      _audioService.cancelRecording();
    }
    super.dispose();
  }
}
