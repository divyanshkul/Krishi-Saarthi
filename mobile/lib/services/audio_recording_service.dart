import 'dart:io';
import 'package:flutter/foundation.dart';
import 'package:record/record.dart';
import 'package:permission_handler/permission_handler.dart';

class AudioRecordingService {
  static final AudioRecordingService _instance = AudioRecordingService._internal();
  factory AudioRecordingService() => _instance;
  AudioRecordingService._internal();

  final AudioRecorder _recorder = AudioRecorder();
  bool _isRecording = false;
  String? _currentRecordingPath;

  bool get isRecording => _isRecording;
  String? get currentRecordingPath => _currentRecordingPath;

  Future<bool> hasPermission() async {
    final status = await Permission.microphone.status;
    return status == PermissionStatus.granted;
  }

  Future<bool> requestPermission() async {
    if (await hasPermission()) return true;
    
    final status = await Permission.microphone.request();
    return status == PermissionStatus.granted;
  }

  Future<bool> startRecording() async {
    try {
      if (_isRecording) {
        debugPrint('Already recording');
        return false;
      }

      if (!await requestPermission()) {
        debugPrint('Microphone permission not granted');
        return false;
      }

      // Save to public Downloads folder so it's accessible via Files app
      final Directory downloadsDir = Directory('/storage/emulated/0/Download');
      final String timestamp = DateTime.now().millisecondsSinceEpoch.toString();
      final String fileName = 'recording_$timestamp.wav';
      final String filePath = '${downloadsDir.path}/$fileName';

      const config = RecordConfig(
        encoder: AudioEncoder.wav,
        bitRate: 128000,
        sampleRate: 44100,
        numChannels: 1,
      );

      await _recorder.start(config, path: filePath);
      
      _isRecording = true;
      _currentRecordingPath = filePath;
      
      debugPrint('Started recording: $filePath');
      return true;
    } catch (e) {
      debugPrint('Error starting recording: $e');
      return false;
    }
  }

  Future<String?> stopRecording() async {
    try {
      if (!_isRecording) {
        debugPrint('Not currently recording');
        return null;
      }

      await _recorder.stop();
      
      _isRecording = false;
      final String? savedPath = _currentRecordingPath;
      _currentRecordingPath = null;
      
      debugPrint('Stopped recording: $savedPath');
      return savedPath;
    } catch (e) {
      debugPrint('Error stopping recording: $e');
      _isRecording = false;
      _currentRecordingPath = null;
      return null;
    }
  }

  Future<void> cancelRecording() async {
    try {
      if (!_isRecording) return;

      await _recorder.stop();
      
      if (_currentRecordingPath != null) {
        final file = File(_currentRecordingPath!);
        if (await file.exists()) {
          await file.delete();
          debugPrint('Cancelled and deleted recording: $_currentRecordingPath');
        }
      }
      
      _isRecording = false;
      _currentRecordingPath = null;
    } catch (e) {
      debugPrint('Error cancelling recording: $e');
      _isRecording = false;
      _currentRecordingPath = null;
    }
  }

  Future<List<String>> getAllRecordings() async {
    try {
      final Directory downloadsDir = Directory('/storage/emulated/0/Download');
      final List<FileSystemEntity> files = downloadsDir.listSync();
      
      final List<String> recordingPaths = files
          .whereType<File>()
          .where((file) => file.path.contains('recording_') && file.path.endsWith('.wav'))
          .map((file) => file.path)
          .toList();
      
      recordingPaths.sort((a, b) => b.compareTo(a)); // Sort by newest first
      return recordingPaths;
    } catch (e) {
      debugPrint('Error getting recordings: $e');
      return [];
    }
  }

  Future<bool> deleteRecording(String path) async {
    try {
      final file = File(path);
      if (await file.exists()) {
        await file.delete();
        debugPrint('Deleted recording: $path');
        return true;
      }
      return false;
    } catch (e) {
      debugPrint('Error deleting recording: $e');
      return false;
    }
  }

  void dispose() {
    _recorder.dispose();
  }
}