import 'package:flutter/material.dart';

import 'app_theme.dart';
import 'splash_screen.dart';

void main() {
  runApp(const ChungViApp());
}

class ChungViApp extends StatelessWidget {
  const ChungViApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'Chung Ví',
      theme: AppTheme.lightTheme,
      home: const SplashScreen(),
    );
  }
}