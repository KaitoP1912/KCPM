import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';

class ApiService {
  static String get baseUrl {
    if (kIsWeb) {
      return "http://127.0.0.1:8000/api";
    }

    return "http://192.168.0.5:8000/api";
  }

  static final Dio dio = Dio(
    BaseOptions(
      baseUrl: baseUrl,
      connectTimeout: const Duration(seconds: 8),
      receiveTimeout: const Duration(seconds: 8),
      sendTimeout: const Duration(seconds: 8),
      headers: {
        "Content-Type": "application/json",
      },
    ),
  );

  static Future<void> setToken(
    String token, {
    String? email,
  }) async {
    final prefs = await SharedPreferences.getInstance();

    await prefs.setString("access_token", token);

    if (email != null && email.isNotEmpty) {
      await prefs.setString("user_email", email);
    }

    dio.options.headers["Authorization"] = "Bearer $token";
  }

  static Future<String?> getSavedEmail() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString("user_email");
  }

  static Future<String?> loadToken() async {
    final prefs = await SharedPreferences.getInstance();

    final token = prefs.getString("access_token");

    if (token != null && token.isNotEmpty) {
      dio.options.headers["Authorization"] = "Bearer $token";
      return token;
    }

    dio.options.headers.remove("Authorization");

    return null;
  }

  static Future<void> logout() async {
    final prefs = await SharedPreferences.getInstance();

    await prefs.remove("access_token");
    await prefs.remove("user_email");

    dio.options.headers.remove("Authorization");
  }

  static bool isUnauthorized(Object error) {
    return error is DioException && error.response?.statusCode == 401;
  }

  static Future<bool> checkAuth() async {
    final token = await loadToken();

    if (token == null || token.isEmpty) {
      return false;
    }

    try {
      await dio.get('/households/');
      return true;
    } catch (e) {
      if (isUnauthorized(e)) {
        await logout();
      }

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
    return response.data;
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

  static Future<List<dynamic>> getHouseholdExpenses(
    String householdId,
  ) async {
    final response = await dio.get(
      '/expenses/household/$householdId/',
    );

    return response.data;
  }

  static Future<List<dynamic>> getHouseholdDebts(
    String householdId,
  ) async {
    final response = await dio.get(
      '/expenses/household/$householdId/debts/',
    );

    return response.data;
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
}