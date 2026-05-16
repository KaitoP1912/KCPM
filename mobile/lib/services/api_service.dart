import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'dart:io';

class ApiService {
  static const String apiHost = String.fromEnvironment(
    'API_HOST',
    defaultValue: '192.168.0.5',
  );

  static String get baseUrl {
    if (kIsWeb) {
      return 'http://127.0.0.1:8000/api';
    }

    return 'http://$apiHost:8000/api';
  }

  static final Dio dio = Dio(
    BaseOptions(
      baseUrl: baseUrl,
      connectTimeout: const Duration(seconds: 10),
      receiveTimeout: const Duration(seconds: 10),
      sendTimeout: const Duration(seconds: 10),
      headers: {
        "Content-Type": "application/json",
      },
    ),
  );

  static bool _isRefreshing = false;

  static Future<void> init() async {
    await loadToken();

    dio.interceptors.clear();

    dio.interceptors.add(
      InterceptorsWrapper(
        onError: (error, handler) async {
          final statusCode = error.response?.statusCode;
          final requestOptions = error.requestOptions;
          final isRefreshApi = requestOptions.path.contains('/auth/refresh/');

          if (statusCode == 401 && !isRefreshApi) {
            if (_isRefreshing) {
              return handler.next(error);
            }

            _isRefreshing = true;
            final refreshed = await refreshAccessToken();
            _isRefreshing = false;

            if (refreshed) {
              try {
                final token = await getAccessToken();

                requestOptions.headers['Authorization'] = 'Bearer $token';

                final clonedResponse = await dio.fetch(requestOptions);

                return handler.resolve(clonedResponse);
              } catch (_) {}
            } else {
              await logout();
            }
          }

          return handler.next(error);
        },
      ),
    );
  }

  static Future<void> saveTokens({
    required String access,
    required String refresh,
    String? email,
  }) async {
    final prefs = await SharedPreferences.getInstance();

    await prefs.setString('access_token', access);
    await prefs.setString('refresh_token', refresh);

    if (email != null) {
      await prefs.setString('user_email', email);
    }

    dio.options.headers['Authorization'] = 'Bearer $access';
  }

  static Future<String?> getAccessToken() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString('access_token');
  }

  static Future<String?> getRefreshToken() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString('refresh_token');
  }

  static Future<String?> getSavedEmail() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString('user_email');
  }

  static Future<void> loadToken() async {
    final access = await getAccessToken();

    if (access != null && access.isNotEmpty) {
      dio.options.headers['Authorization'] = 'Bearer $access';
    }
  }

  static Future<bool> refreshAccessToken() async {
    try {
      final refresh = await getRefreshToken();

      if (refresh == null || refresh.isEmpty) {
        return false;
      }

      final response = await Dio().post(
        '$baseUrl/auth/refresh/',
        data: {
          'refresh': refresh,
        },
      );

      final newAccess = response.data['access'];

      final prefs = await SharedPreferences.getInstance();

      await prefs.setString('access_token', newAccess);

      dio.options.headers['Authorization'] = 'Bearer $newAccess';

      return true;
    } catch (_) {
      return false;
    }
  }

  static Future<void> logout() async {
    final prefs = await SharedPreferences.getInstance();

    await prefs.clear();

    dio.options.headers.remove('Authorization');
  }

  static Future<bool> checkAuth() async {
    final access = await getAccessToken();

    if (access == null || access.isEmpty) {
      return false;
    }

    try {
      await dio.get('/households/');
      return true;
    } catch (e) {
      final refreshed = await refreshAccessToken();

      if (refreshed) {
        try {
          await dio.get('/households/');
          return true;
        } catch (_) {}
      }

      await logout();
      return false;
    }
  }

  static Future<Response> login({
    required String email,
    required String password,
  }) async {
    return dio.post(
      "/auth/login/",
      data: {
        "email": email,
        "password": password,
      },
    );
  }

  static Future<List<dynamic>> getHouseholds() async {
    final response = await dio.get('/households/');
    return List<dynamic>.from(response.data);
  }

  static Future<Map<String, dynamic>> getHouseholdDetail(
    String householdId,
  ) async {
    final response = await dio.get('/households/$householdId/');
    return Map<String, dynamic>.from(response.data);
  }

  static Future<void> createHousehold({
    required String name,
    required String description,
  }) async {
    await dio.post(
      '/households/',
      data: {
        'name': name,
        'description': description,
      },
    );
  }

  static Future<void> addMemberToHousehold({
    required String householdId,
    required String email,
    String role = 'member',
  }) async {
    await dio.post(
      '/households/$householdId/members/add/',
      data: {
        'email': email,
        'role': role,
      },
    );
  }

  static Future<List<dynamic>> getAllActivities() async {
    final response = await dio.get('/households/activities/');
    return List<dynamic>.from(response.data);
  }

  static Future<List<dynamic>> getActivities(
    String householdId,
  ) async {
    final response = await dio.get(
      '/households/$householdId/activities/',
    );

    return List<dynamic>.from(response.data);
  }

  static Future<List<dynamic>> getHouseholdExpenses(
    String householdId,
  ) async {
    final response = await dio.get(
      '/expenses/household/$householdId/',
    );

    return List<dynamic>.from(response.data);
  }

  static Future<List<dynamic>> getHouseholdDebts(
    String householdId,
  ) async {
    final response = await dio.get(
      '/expenses/household/$householdId/debts/',
    );

    return List<dynamic>.from(response.data);
  }

  static Future<List<dynamic>> getAllDebtsFromHouseholds(
    List<String> householdIds,
  ) async {
    List<dynamic> allDebts = [];

    for (final id in householdIds) {
      try {
        final response = await dio.get(
          '/expenses/household/$id/debts/',
        );

        if (response.data is List) {
          allDebts.addAll(response.data);
        }
      } catch (_) {}
    }

    return allDebts;
  }

  static Future<void> createExpense({
    required String householdId,
    required String title,
    required double amount,
    required int payer,
    required List<int> participants,
    String note = '',
  }) async {
    await dio.post(
      '/expenses/',
      data: {
        'household': householdId,
        'title': title,
        'amount': amount.toInt(),
        'payer': payer,
        'participants': participants
            .map(
              (userId) => {
                'user_id': userId,
              },
            )
            .toList(),
        'note': note,
        'split_type': 'equal',
      },
    );
  }

  static Future<void> saveFCMToken(
    String token,
  ) async {
    await dio.post(
      '/notifications/save-fcm-token/',
      data: {
        'token': token,
        'device_type': 'android',
      },
    );
  }

  static Future<List<dynamic>> getNotifications() async {
    final response = await dio.get('/notifications/');
    return List<dynamic>.from(response.data);
  }

  static Future<int> getUnreadNotificationCount() async {
    final response = await dio.get('/notifications/unread-count/');
    return response.data['unread_count'] ?? 0;
  }

  static Future<void> markNotificationAsRead(
    String notificationId,
  ) async {
    await dio.patch(
      '/notifications/$notificationId/read/',
    );
  }

  static Future<void> markAllNotificationsAsRead() async {
    await dio.patch('/notifications/mark-all-read/');
  }
}