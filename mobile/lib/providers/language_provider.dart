import 'package:flutter/material.dart';

class LanguageProvider with ChangeNotifier {
  Locale _currentLocale = const Locale('hi');

  Locale get currentLocale => _currentLocale;

  void toggleLocale() {
    if (_currentLocale.languageCode == 'hi') {
      _currentLocale = const Locale('en');
    } else {
      _currentLocale = const Locale('hi');
    }
    notifyListeners();
  }
}
