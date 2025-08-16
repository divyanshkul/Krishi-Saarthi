import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../i18n.dart';

class LanguageProvider with ChangeNotifier {
  Locale _currentLocale = const Locale('hi');
  static const String _languageKey = 'selected_language';

  Locale get currentLocale => _currentLocale;
  bool get isHindi => _currentLocale.languageCode == 'hi';
  bool get isEnglish => _currentLocale.languageCode == 'en';
  
  String get currentLanguageDisplay => isHindi ? 'हिं' : 'EN';
  String get toggleLanguageDisplay => isHindi ? 'EN' : 'हिं';

  LanguageProvider() {
    _loadSavedLanguage();
  }

  void toggleLocale() async {
    if (_currentLocale.languageCode == 'hi') {
      _currentLocale = const Locale('en');
    } else {
      _currentLocale = const Locale('hi');
    }
    await _saveLanguage();
    notifyListeners();
  }

  void setLocale(String languageCode) async {
    if (languageCode == 'hi' || languageCode == 'en') {
      _currentLocale = Locale(languageCode);
      await _saveLanguage();
      notifyListeners();
    }
  }

  String translate(String key) {
    return translations[_currentLocale.languageCode]?[key] ?? key;
  }

  Future<void> _loadSavedLanguage() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final savedLanguage = prefs.getString(_languageKey);
      if (savedLanguage != null && (savedLanguage == 'hi' || savedLanguage == 'en')) {
        _currentLocale = Locale(savedLanguage);
        notifyListeners();
      }
    } catch (e) {
      debugPrint('Error loading saved language: $e');
    }
  }

  Future<void> _saveLanguage() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString(_languageKey, _currentLocale.languageCode);
    } catch (e) {
      debugPrint('Error saving language: $e');
    }
  }
}
