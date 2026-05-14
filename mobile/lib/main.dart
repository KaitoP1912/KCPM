import 'package:flutter/material.dart';

import 'app_theme.dart';
import 'services/api_service.dart';
import 'splash_screen.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();

  await ApiService.init();

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