import 'package:flutter/material.dart';

class Suggestion {
  final String title;
  final String description;
  final IconData icon;
  final Color iconColor;
  final List<Widget>? actions;

  Suggestion({
    required this.title,
    required this.description,
    required this.icon,
    this.iconColor = Colors.blue,
    this.actions,
  });
}
