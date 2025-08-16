import 'dart:io';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:krishi_saarthi_mobile/screens/voice_recording_screen.dart';
import '../widgets/app_header.dart';
import '../widgets/chat_response.dart';
import '../widgets/photo_source_dialog.dart';
import '../providers/recording_provider.dart';
import '../providers/photo_provider.dart';
import '../providers/text_provider.dart';
import '../providers/language_provider.dart';

class ChatPage extends StatefulWidget {
  const ChatPage({super.key});

  @override
  State<ChatPage> createState() => _ChatPageState();
}

class _ChatPageState extends State<ChatPage> {
  final TextEditingController _textController = TextEditingController();

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
          Consumer3<RecordingProvider, PhotoProvider, TextProvider>(
            builder: (context, recordingProvider, photoProvider, textProvider, child) {
              return Column(
                children: [
                  if (recordingProvider.hasRecording) _buildRecordingAttachment(context, recordingProvider),
                  if (photoProvider.hasPhoto) _buildPhotoAttachment(context, photoProvider),
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

  Widget _buildPhotoAttachment(BuildContext context, PhotoProvider photoProvider) {
    final photoFile = photoProvider.getPhotoFile();
    
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      decoration: BoxDecoration(
        color: Colors.blue.shade50,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.blue.shade200),
      ),
      child: Row(
        children: [
          Container(
            width: 40,
            height: 40,
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(6),
              border: Border.all(color: Colors.blue.shade200),
            ),
            child: ClipRRect(
              borderRadius: BorderRadius.circular(6),
              child: photoFile != null && photoFile.existsSync()
                  ? Image.file(
                      photoFile,
                      fit: BoxFit.cover,
                    )
                  : Icon(
                      Icons.image,
                      color: Colors.blue.shade400,
                      size: 20,
                    ),
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              photoProvider.getPhotoDisplayName() ?? 'Photo attached',
              style: TextStyle(
                color: Colors.blue.shade700,
                fontSize: 14,
                fontWeight: FontWeight.w500,
              ),
            ),
          ),
          GestureDetector(
            onTap: () => photoProvider.clearPhoto(),
            child: Icon(
              Icons.close,
              color: Colors.blue.shade600,
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
          Consumer<PhotoProvider>(
            builder: (context, photoProvider, child) {
              return IconButton(
                onPressed: () => _handleCameraPressed(context),
                icon: const Icon(Icons.camera_alt),
                color: photoProvider.hasPhoto ? Colors.blue.shade700 : Colors.grey,
              );
            },
          ),
          Expanded(
            child: Consumer4<RecordingProvider, PhotoProvider, TextProvider, LanguageProvider>(
              builder: (context, recordingProvider, photoProvider, textProvider, languageProvider, child) {
                final bool bothAttached = recordingProvider.hasRecording && photoProvider.hasPhoto;
                
                return TextField(
                  controller: _textController,
                  enabled: !bothAttached,
                  maxLines: bothAttached ? 2 : 1,
                  decoration: InputDecoration(
                    hintText: bothAttached 
                        ? 'Audio + Photo attached\nTap send to process'
                        : languageProvider.translate('askYourQuestion'),
                    hintStyle: TextStyle(
                      fontSize: bothAttached ? 12 : 14,
                      color: bothAttached ? Colors.orange.shade600 : Colors.grey.shade600,
                      fontStyle: bothAttached ? FontStyle.italic : FontStyle.normal,
                    ),
                    border: InputBorder.none,
                  ),
                  style: TextStyle(
                    color: bothAttached ? Colors.grey.shade400 : Colors.black,
                  ),
                  onChanged: (text) {
                    textProvider.setText(text);
                  },
                );
              },
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
          Consumer3<RecordingProvider, PhotoProvider, TextProvider>(
            builder: (context, recordingProvider, photoProvider, textProvider, child) {
              final bool isProcessing = recordingProvider.isProcessing || textProvider.isProcessing;
              final bool hasText = textProvider.hasText;
              final bool hasAudio = recordingProvider.hasRecording;
              final bool hasPhoto = photoProvider.hasPhoto;
              final bool isPhotoOnly = hasPhoto && !hasText && !hasAudio;
              final bool isDisabled = isProcessing || isPhotoOnly;
              
              return GestureDetector(
                onTap: isDisabled ? null : () => _handleSend(context, recordingProvider, photoProvider, textProvider),
                child: CircleAvatar(
                  backgroundColor: isDisabled 
                      ? Colors.grey 
                      : Colors.green,
                  child: isProcessing
                      ? SizedBox(
                          width: 20,
                          height: 20,
                          child: CircularProgressIndicator(
                            color: Colors.white,
                            strokeWidth: 2,
                          ),
                        )
                      : Icon(
                          Icons.send, 
                          color: isDisabled ? Colors.grey.shade400 : Colors.white,
                        ),
                ),
              );
            },
          ),
        ],
      ),
    );
  }

  void _handleCameraPressed(BuildContext context) async {
    final source = await PhotoSourceDialog.show(context);
    
    if (source != null && context.mounted) {
      final photoProvider = Provider.of<PhotoProvider>(context, listen: false);
      bool success = false;
      
      try {
        if (source == 'camera') {
          success = await photoProvider.capturePhoto();
        } else if (source == 'gallery') {
          success = await photoProvider.selectFromGallery();
        }
        
        if (!success && context.mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('Failed to select photo'),
              backgroundColor: Colors.red,
            ),
          );
        }
      } catch (e) {
        if (context.mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text('Error: $e'),
              backgroundColor: Colors.red,
            ),
          );
        }
      }
    }
  }

  void _handleSend(BuildContext context, RecordingProvider recordingProvider, PhotoProvider photoProvider, TextProvider textProvider) async {
    // Prevent sending if already processing
    if (recordingProvider.isProcessing || textProvider.isProcessing) return;

    final bool hasText = textProvider.hasText;
    final bool hasAudio = recordingProvider.hasRecording;
    final bool hasPhoto = photoProvider.hasPhoto;

    debugPrint('🔍 Send button pressed - Text: $hasText, Audio: $hasAudio, Photo: $hasPhoto');

    // Use Case 1 & 2: Text (with or without audio/photo) - Text takes priority
    if (hasText) {
      if (hasPhoto) {
        debugPrint('📝📷 Processing text + photo (ignoring audio if present)');
        await textProvider.processText(photoProvider.currentPhotoPath);
      } else {
        debugPrint('📝 Processing text only (ignoring audio if present)');
        await textProvider.processText();
      }
      
      // Handle result
      if (textProvider.processingState == TextProcessingState.success) {
        debugPrint('✅ Text AI Response: ${textProvider.aiResponse}');
        _textController.clear(); // Clear text field
        if (hasPhoto) photoProvider.clearPhoto(); // Clear photo attachment
        if (hasAudio) recordingProvider.clearRecording(); // Clear audio if present
      } else if (textProvider.processingState == TextProcessingState.error && context.mounted) {
        _showError(context, 'Text processing error: ${textProvider.processingError}');
      }
    }
    // Use Case 3: Audio + Photo  
    else if (hasAudio && hasPhoto) {
      debugPrint('🎵📷 Processing audio + photo');
      await recordingProvider.processAudio(photoProvider.currentPhotoPath);
      
      if (recordingProvider.processingState == ProcessingState.success) {
        debugPrint('✅ Audio+Photo AI Response: ${recordingProvider.aiResponse}');
        if (hasText) _textController.clear(); // Clear text if present
        photoProvider.clearPhoto(); // Clear photo attachment
      } else if (recordingProvider.processingState == ProcessingState.error && context.mounted) {
        _showError(context, 'Audio+Photo processing error: ${recordingProvider.processingError}');
      }
    }
    // Use Case 4: Audio Only
    else if (hasAudio && !hasPhoto) {
      debugPrint('🎵 Processing audio only');
      await recordingProvider.processAudio();
      
      if (recordingProvider.processingState == ProcessingState.success) {
        debugPrint('✅ Audio AI Response: ${recordingProvider.aiResponse}');
        if (hasText) _textController.clear(); // Clear text if present
      } else if (recordingProvider.processingState == ProcessingState.error && context.mounted) {
        _showError(context, 'Audio processing error: ${recordingProvider.processingError}');
      }
    }
    else {
      debugPrint('❌ No content to send');
      _showError(context, 'Please enter text, record audio, or attach a photo');
    }
  }

  void _showError(BuildContext context, String message) {
    if (context.mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(message),
          backgroundColor: Colors.red,
        ),
      );
    }
  }

  @override
  void dispose() {
    _textController.dispose();
    super.dispose();
  }
}
