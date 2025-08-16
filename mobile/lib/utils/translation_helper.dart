import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/language_provider.dart';

class T {
  static String of(BuildContext context, String key) {
    return Provider.of<LanguageProvider>(context, listen: false).translate(key);
  }
}

extension TranslationExtension on BuildContext {
  String t(String key) {
    return Provider.of<LanguageProvider>(this, listen: false).translate(key);
  }
}