import 'package:dio/dio.dart';
import 'package:shared_preferences/shared_preferences.dart';

class ApiService {
  static final Dio dio = Dio(
    BaseOptions(
      baseUrl: "http://192.168.0.5:8000/api",
      headers: {
        "Content-Type": "application/json",
      },
    ),
  );

  static Future<void> setToken(String token) async {
    final prefs = await SharedPreferences.getInstance();

    await prefs.setString("token", token);

    dio.options.headers["Authorization"] = "Bearer $token";
  }

  static Future<void> loadToken() async {
    final prefs = await SharedPreferences.getInstance();

    final token = prefs.getString("token");

    if (token != null) {
      dio.options.headers["Authorization"] = "Bearer $token";
    }
  }

  static Future<Response> login({
    required String email,
    required String password,
  }) async {
    return await dio.post(
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
}