import 'dart:async';

import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';

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
        'Content-Type': 'application/json',
      },
    ),
  );

  static Future<bool>? _refreshTokenFuture;

  static Future<void> init() async {
    await loadToken();

    dio.interceptors.clear();

    dio.interceptors.add(
      InterceptorsWrapper(
        onRequest: (options, handler) async {
          final access = await getAccessToken();

          if (access != null && access.isNotEmpty) {
            options.headers['Authorization'] = 'Bearer $access';
          }

          return handler.next(options);
        },
        onError: (error, handler) async {
          final statusCode = error.response?.statusCode;
          final requestOptions = error.requestOptions;

          final isAuthApi =
              requestOptions.path.contains('/auth/login/') ||
              requestOptions.path.contains('/auth/register/') ||
              requestOptions.path.contains('/auth/refresh/');

          final alreadyRetried =
              requestOptions.extra['alreadyRetried'] == true;

          if (statusCode == 401 && !isAuthApi && !alreadyRetried) {
            final refreshed = await _refreshTokenSafely();

            if (refreshed) {
              try {
                final access = await getAccessToken();

                final retryOptions = Options(
                  method: requestOptions.method,
                  headers: {
                    ...requestOptions.headers,
                    if (access != null && access.isNotEmpty)
                      'Authorization': 'Bearer $access',
                  },
                  responseType: requestOptions.responseType,
                  contentType: requestOptions.contentType,
                  followRedirects: requestOptions.followRedirects,
                  validateStatus: requestOptions.validateStatus,
                  receiveDataWhenStatusError:
                      requestOptions.receiveDataWhenStatusError,
                  extra: {
                    ...requestOptions.extra,
                    'alreadyRetried': true,
                  },
                );

                final response = await dio.request<dynamic>(
                  requestOptions.path,
                  data: requestOptions.data,
                  queryParameters: requestOptions.queryParameters,
                  options: retryOptions,
                  cancelToken: requestOptions.cancelToken,
                  onSendProgress: requestOptions.onSendProgress,
                  onReceiveProgress: requestOptions.onReceiveProgress,
                );

                return handler.resolve(response);
              } catch (e) {
                return handler.next(error);
              }
            }

            await logout();
          }

          return handler.next(error);
        },
      ),
    );
  }

  static Future<bool> _refreshTokenSafely() async {
    _refreshTokenFuture ??= refreshAccessToken();

    try {
      return await _refreshTokenFuture!;
    } finally {
      _refreshTokenFuture = null;
    }
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

      final refreshDio = Dio(
        BaseOptions(
          connectTimeout: const Duration(seconds: 10),
          receiveTimeout: const Duration(seconds: 10),
          sendTimeout: const Duration(seconds: 10),
          headers: {
            'Content-Type': 'application/json',
          },
        ),
      );

      final response = await refreshDio.post(
        '$baseUrl/auth/refresh/',
        data: {
          'refresh': refresh,
        },
      );

      final newAccess = response.data['access'];

      if (newAccess == null || newAccess.toString().isEmpty) {
        return false;
      }

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

    await prefs.remove('access_token');
    await prefs.remove('refresh_token');
    await prefs.remove('user_email');

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
    } catch (_) {
      final refreshed = await _refreshTokenSafely();

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
      '/auth/login/',
      data: {
        'email': email,
        'password': password,
      },
    );
  }

  static Future<Response> register({
    required String email,
    required String username,
    required String fullName,
    required String phoneNumber,
    required String password,
  }) async {
    return dio.post(
      '/auth/register/',
      data: {
        'email': email,
        'username': username,
        'full_name': fullName,
        'phone_number': phoneNumber,
        'password': password,
      },
    );
  }

  static Future<Response> changePassword({
    required String oldPassword,
    required String newPassword,
    required String confirmPassword,
  }) async {
    return dio.post(
      '/auth/change-password/',
      data: {
        'old_password': oldPassword,
        'new_password': newPassword,
        'confirm_password': confirmPassword,
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
    final List<dynamic> allDebts = [];

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

  static Future<Map<String, dynamic>> getProfile() async {
    final response = await dio.get('/auth/profile/');
    return Map<String, dynamic>.from(response.data);
  }

  static Future<Map<String, dynamic>> updateProfile({
    required String fullName,
    required String phoneNumber,
    required String bankName,
    required String bankAccountNumber,
    required String bankAccountHolder,
  }) async {
    final response = await dio.patch(
      '/auth/profile/',
      data: {
        'full_name': fullName,
        'phone_number': phoneNumber,
        'bank_name': bankName,
        'bank_account_number': bankAccountNumber,
        'bank_account_holder': bankAccountHolder,
      },
    );

    return Map<String, dynamic>.from(response.data);
  }
}