import 'package:dio/dio.dart';
import 'package:flutter/material.dart';

import 'app_theme.dart';
import 'login_screen.dart';
import 'services/api_service.dart';

class RegisterScreen extends StatefulWidget {
  const RegisterScreen({super.key});

  @override
  State<RegisterScreen> createState() =>
      _RegisterScreenState();
}

class _RegisterScreenState extends State<RegisterScreen> {
  final fullNameController = TextEditingController();
  final emailController = TextEditingController();
  final phoneController = TextEditingController();
  final passwordController = TextEditingController();
  final confirmPasswordController = TextEditingController();

  bool isLoading = false;
  bool hidePassword = true;
  bool hideConfirmPassword = true;

  @override
  void dispose() {
    fullNameController.dispose();
    emailController.dispose();
    phoneController.dispose();
    passwordController.dispose();
    confirmPasswordController.dispose();
    super.dispose();
  }

  bool isValidEmail(String email) {
    return RegExp(
      r'^[\w\.-]+@([\w-]+\.)+[\w-]{2,4}$',
    ).hasMatch(email);
  }

  Future<void> register() async {
    final fullName = fullNameController.text.trim();
    final email = emailController.text.trim().toLowerCase();
    final phone = phoneController.text.trim();
    final password = passwordController.text.trim();
    final confirmPassword =
        confirmPasswordController.text.trim();

    if (fullName.isEmpty ||
        email.isEmpty ||
        phone.isEmpty ||
        password.isEmpty ||
        confirmPassword.isEmpty) {
      showMessage('Vui lòng nhập đầy đủ thông tin');
      return;
    }

    if (!isValidEmail(email)) {
      showMessage('Email không hợp lệ');
      return;
    }

    if (password.length < 8) {
      showMessage('Mật khẩu phải có ít nhất 8 ký tự');
      return;
    }

    if (password != confirmPassword) {
      showMessage('Mật khẩu xác nhận không khớp');
      return;
    }

    try {
      setState(() {
        isLoading = true;
      });

      await ApiService.register(
        email: email,
        username: email,
        fullName: fullName,
        phoneNumber: phone,
        password: password,
      );

      if (!mounted) return;

      showMessage('Đăng ký thành công. Vui lòng đăng nhập.');

      Navigator.pushReplacement(
        context,
        MaterialPageRoute(
          builder: (_) => const LoginScreen(),
        ),
      );
    } on DioException catch (e) {
      final data = e.response?.data;

      if (data is Map) {
        final firstError = data.values.isNotEmpty
            ? data.values.first.toString()
            : 'Đăng ký thất bại';

        showMessage(firstError);
      } else {
        showMessage('Đăng ký thất bại');
      }
    } catch (_) {
      showMessage('Không thể kết nối máy chủ');
    } finally {
      if (mounted) {
        setState(() {
          isLoading = false;
        });
      }
    }
  }

  void showMessage(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        behavior: SnackBarBehavior.floating,
      ),
    );
  }

  Widget buildInput({
    required TextEditingController controller,
    required String hint,
    required IconData icon,
    bool obscure = false,
    Widget? suffixIcon,
    TextInputType? keyboardType,
    TextInputAction? textInputAction,
    void Function(String)? onSubmitted,
  }) {
    return TextField(
      controller: controller,
      obscureText: obscure,
      keyboardType: keyboardType,
      textInputAction: textInputAction,
      onSubmitted: onSubmitted,
      style: const TextStyle(
        fontSize: 15,
        fontWeight: FontWeight.w600,
        color: AppColors.textDark,
      ),
      decoration: InputDecoration(
        hintText: hint,
        prefixIcon: Icon(
          icon,
          color: AppColors.textLight,
          size: 21,
        ),
        suffixIcon: suffixIcon,
      ),
    );
  }

  Widget buildRegisterButton() {
    return SizedBox(
      width: double.infinity,
      height: 58,
      child: ElevatedButton(
        onPressed: isLoading ? null : register,
        child: isLoading
            ? const SizedBox(
                width: 22,
                height: 22,
                child: CircularProgressIndicator(
                  strokeWidth: 2.5,
                  color: Colors.white,
                ),
              )
            : const Text(
                'Đăng ký',
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.w800,
                ),
              ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: const Text('Tạo tài khoản'),
      ),
      body: SafeArea(
        child: Center(
          child: SingleChildScrollView(
            padding: const EdgeInsets.symmetric(
              horizontal: 24,
              vertical: 20,
            ),
            child: ConstrainedBox(
              constraints: const BoxConstraints(
                maxWidth: 410,
              ),
              child: Column(
                children: [
                  const Text(
                    'Tham gia Chung Ví',
                    style: TextStyle(
                      fontSize: 30,
                      fontWeight: FontWeight.w900,
                      color: AppColors.textDark,
                      letterSpacing: -0.8,
                    ),
                  ),
                  const SizedBox(height: 8),
                  const Text(
                    'Tạo tài khoản để quản lý chia tiền nhóm dễ dàng hơn.',
                    textAlign: TextAlign.center,
                    style: TextStyle(
                      color: AppColors.textLight,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  const SizedBox(height: 32),
                  buildInput(
                    controller: fullNameController,
                    hint: 'Họ và tên',
                    icon: Icons.badge_rounded,
                    textInputAction: TextInputAction.next,
                  ),
                  const SizedBox(height: 14),
                  buildInput(
                    controller: emailController,
                    hint: 'Email',
                    icon: Icons.alternate_email_rounded,
                    keyboardType: TextInputType.emailAddress,
                    textInputAction: TextInputAction.next,
                  ),
                  const SizedBox(height: 14),
                  buildInput(
                    controller: phoneController,
                    hint: 'Số điện thoại',
                    icon: Icons.phone_rounded,
                    keyboardType: TextInputType.phone,
                    textInputAction: TextInputAction.next,
                  ),
                  const SizedBox(height: 14),
                  buildInput(
                    controller: passwordController,
                    hint: 'Mật khẩu',
                    icon: Icons.lock_outline_rounded,
                    obscure: hidePassword,
                    textInputAction: TextInputAction.next,
                    suffixIcon: IconButton(
                      onPressed: () {
                        setState(() {
                          hidePassword = !hidePassword;
                        });
                      },
                      icon: Icon(
                        hidePassword
                            ? Icons.visibility_off_outlined
                            : Icons.visibility_outlined,
                        color: AppColors.textLight,
                      ),
                    ),
                  ),
                  const SizedBox(height: 14),
                  buildInput(
                    controller: confirmPasswordController,
                    hint: 'Xác nhận mật khẩu',
                    icon: Icons.lock_reset_rounded,
                    obscure: hideConfirmPassword,
                    textInputAction: TextInputAction.done,
                    onSubmitted: (_) => register(),
                    suffixIcon: IconButton(
                      onPressed: () {
                        setState(() {
                          hideConfirmPassword =
                              !hideConfirmPassword;
                        });
                      },
                      icon: Icon(
                        hideConfirmPassword
                            ? Icons.visibility_off_outlined
                            : Icons.visibility_outlined,
                        color: AppColors.textLight,
                      ),
                    ),
                  ),
                  const SizedBox(height: 24),
                  buildRegisterButton(),
                  const SizedBox(height: 20),
                  TextButton(
                    onPressed: isLoading
                        ? null
                        : () {
                            Navigator.pop(context);
                          },
                    child: const Text(
                      'Đã có tài khoản? Đăng nhập',
                      style: TextStyle(
                        fontWeight: FontWeight.w800,
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}