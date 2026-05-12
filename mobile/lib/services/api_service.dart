import 'package:dio/dio.dart';

class ApiService {
  static final Dio dio = Dio(
    BaseOptions(
      baseUrl: "http://127.0.0.1:8000/api",
      headers: {
        "Content-Type": "application/json",

        "Authorization":
            "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzc4NjE2NDk0LCJpYXQiOjE3Nzg2MTYxOTQsImp0aSI6Ijc0ODhhN2E4ODJhYzQ2NWY4MWFiMTRiMGU0NzBhZTIzIiwidXNlcl9pZCI6IjEifQ.9OYHnLUjsDR8SoJ5YUwgUbI4L4o5aXIYJzlID1TdYqM",
      },
    ),
  );

  static Future<List<dynamic>> getHouseholds() async {
    final response = await dio.get('/households/');

    return response.data;
  }
}