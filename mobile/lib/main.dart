import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_messaging/firebase_messaging.dart';

import 'package:flutter/material.dart';

import 'bottom_nav_screen.dart';
import 'firebase_options.dart';
import 'login_screen.dart';
import 'services/api_service.dart';

final GlobalKey<NavigatorState> navigatorKey =
    GlobalKey<NavigatorState>();

Future<void> firebaseMessagingBackgroundHandler(
  RemoteMessage message,
) async {
  await Firebase.initializeApp(
    options: DefaultFirebaseOptions.currentPlatform,
  );
}

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  await Firebase.initializeApp(
    options: DefaultFirebaseOptions.currentPlatform,
  );

  FirebaseMessaging.onBackgroundMessage(
    firebaseMessagingBackgroundHandler,
  );

  await ApiService.init();

  runApp(const MyApp());
}

class MyApp extends StatefulWidget {
  const MyApp({super.key});

  @override
  State<MyApp> createState() => _MyAppState();
}

class _MyAppState extends State<MyApp> {
  bool isCheckingAuth = true;
  bool isLoggedIn = false;

  @override
  void initState() {
    super.initState();

    checkLogin();

    setupFirebaseMessaging();
  }

  Future<void> checkLogin() async {
    final authenticated = await ApiService.checkAuth();

    if (!mounted) return;

    setState(() {
      isLoggedIn = authenticated;
      isCheckingAuth = false;
    });
  }

  Future<void> setupFirebaseMessaging() async {
    debugPrint('SETUP FIREBASE START');
    
    final messaging = FirebaseMessaging.instance;

    await messaging.requestPermission(
      alert: true,
      badge: true,
      sound: true,
    );

    final token = await messaging.getToken();

    debugPrint('FCM TOKEN: $token');

    if (token != null) {
      try {
        await ApiService.saveFCMToken(token);
      } catch (e) {
        debugPrint('SAVE FCM TOKEN ERROR: $e');
      }
    }

    FirebaseMessaging.onMessage.listen((message) {
      debugPrint(
        'FOREGROUND MESSAGE: ${message.notification?.title}',
      );

      final context = navigatorKey.currentContext;

      if (context != null) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              message.notification?.title ??
                  'Thông báo mới',
            ),
          ),
        );
      }
    });

    FirebaseMessaging.onMessageOpenedApp.listen((message) {
      debugPrint('NOTIFICATION CLICKED');
    });
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      navigatorKey: navigatorKey,
      debugShowCheckedModeBanner: false,
      title: 'Chung Ví',
      theme: ThemeData(
        useMaterial3: true,
        colorSchemeSeed: Colors.green,
      ),
      home: isCheckingAuth
          ? const Scaffold(
              body: Center(
                child: CircularProgressIndicator(),
              ),
            )
          : isLoggedIn
              ? const BottomNavScreen()
              : const LoginScreen(),
    );
  }
}