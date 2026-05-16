import 'package:flutter/material.dart';

import 'app_theme.dart';
import 'login_screen.dart';
import 'services/api_service.dart';

class ProfileScreen extends StatefulWidget {
  const ProfileScreen({super.key});

  @override
  State<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> {
  bool isLoading = true;
  bool isSaving = false;

  Map<String, dynamic> profile = {};

  final fullNameController = TextEditingController();
  final phoneController = TextEditingController();
  final bankNameController = TextEditingController();
  final bankAccountNumberController = TextEditingController();
  final bankAccountHolderController = TextEditingController();

  @override
  void initState() {
    super.initState();
    loadProfile();
  }

  @override
  void dispose() {
    fullNameController.dispose();
    phoneController.dispose();
    bankNameController.dispose();
    bankAccountNumberController.dispose();
    bankAccountHolderController.dispose();
    super.dispose();
  }

  Future<void> loadProfile() async {
    try {
      final data = await ApiService.getProfile();

      if (!mounted) return;

      setState(() {
        profile = data;
        isLoading = false;
      });
    } catch (e) {
      if (!mounted) return;

      setState(() {
        isLoading = false;
      });

      showMessage('Không thể tải hồ sơ');
    }
  }

  Future<void> logout() async {
    await ApiService.logout();

    if (!mounted) return;

    Navigator.pushAndRemoveUntil(
      context,
      MaterialPageRoute(
        builder: (_) => const LoginScreen(),
      ),
      (route) => false,
    );
  }

  Future<void> openEditProfile() async {
    fullNameController.text = profile['full_name']?.toString() ?? '';
    phoneController.text = profile['phone_number']?.toString() ?? '';
    bankNameController.text = profile['bank_name']?.toString() ?? '';
    bankAccountNumberController.text =
        profile['bank_account_number']?.toString() ?? '';
    bankAccountHolderController.text =
        profile['bank_account_holder']?.toString() ?? '';

    await showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (_) {
        return StatefulBuilder(
          builder: (sheetContext, setSheetState) {
            Future<void> saveProfile() async {
              setSheetState(() {
                isSaving = true;
              });

              try {
                final updated = await ApiService.updateProfile(
                  fullName: fullNameController.text.trim(),
                  phoneNumber: phoneController.text.trim(),
                  bankName: bankNameController.text.trim(),
                  bankAccountNumber:
                      bankAccountNumberController.text.trim(),
                  bankAccountHolder:
                      bankAccountHolderController.text.trim(),
                );

                if (!mounted || !sheetContext.mounted) return;

                setState(() {
                  profile = updated;
                });

                Navigator.pop(sheetContext);
                showMessage('Đã cập nhật hồ sơ');
              } catch (e) {
                if (!mounted) return;
                showMessage('Cập nhật thất bại');
              } finally {
                if (mounted) {
                  setSheetState(() {
                    isSaving = false;
                  });
                }
              }
            }

            return Container(
              padding: EdgeInsets.only(
                left: 20,
                right: 20,
                top: 20,
                bottom: MediaQuery.of(sheetContext).viewInsets.bottom + 20,
              ),
              decoration: const BoxDecoration(
                color: AppColors.background,
                borderRadius: BorderRadius.vertical(
                  top: Radius.circular(32),
                ),
              ),
              child: SingleChildScrollView(
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Container(
                      width: 46,
                      height: 5,
                      decoration: BoxDecoration(
                        color: AppColors.border,
                        borderRadius: BorderRadius.circular(999),
                      ),
                    ),
                    const SizedBox(height: 22),
                    const Text(
                      'Chỉnh sửa hồ sơ',
                      style: TextStyle(
                        fontSize: 22,
                        fontWeight: FontWeight.w900,
                        color: AppColors.textDark,
                      ),
                    ),
                    const SizedBox(height: 22),
                    buildInput(
                      controller: fullNameController,
                      label: 'Họ và tên',
                      icon: Icons.badge_rounded,
                    ),
                    buildInput(
                      controller: phoneController,
                      label: 'Số điện thoại',
                      icon: Icons.phone_rounded,
                      keyboardType: TextInputType.phone,
                    ),
                    buildInput(
                      controller: bankNameController,
                      label: 'Tên ngân hàng',
                      icon: Icons.account_balance_rounded,
                    ),
                    buildInput(
                      controller: bankAccountNumberController,
                      label: 'Số tài khoản',
                      icon: Icons.credit_card_rounded,
                      keyboardType: TextInputType.number,
                    ),
                    buildInput(
                      controller: bankAccountHolderController,
                      label: 'Chủ tài khoản',
                      icon: Icons.person_outline_rounded,
                    ),
                    const SizedBox(height: 12),
                    SizedBox(
                      height: 56,
                      width: double.infinity,
                      child: ElevatedButton(
                        onPressed: isSaving ? null : saveProfile,
                        child: isSaving
                            ? const SizedBox(
                                width: 22,
                                height: 22,
                                child: CircularProgressIndicator(
                                  color: Colors.white,
                                  strokeWidth: 2.4,
                                ),
                              )
                            : const Text('Lưu thay đổi'),
                      ),
                    ),
                  ],
                ),
              ),
            );
          },
        );
      },
    );
  }

  Widget buildInput({
    required TextEditingController controller,
    required String label,
    required IconData icon,
    TextInputType? keyboardType,
  }) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 14),
      child: TextField(
        controller: controller,
        keyboardType: keyboardType,
        decoration: InputDecoration(
          labelText: label,
          prefixIcon: Icon(icon),
        ),
      ),
    );
  }

  void showMessage(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
      ),
    );
  }

  String valueOf(String key) {
    final value = profile[key];

    if (value == null || value.toString().trim().isEmpty) {
      return 'Chưa cập nhật';
    }

    return value.toString();
  }

  Widget buildSectionTitle(String title) {
    return Text(
      title,
      style: const TextStyle(
        fontSize: 18,
        fontWeight: FontWeight.w900,
        color: AppColors.textDark,
      ),
    );
  }

  Widget buildInfoTile({
    required IconData icon,
    required String title,
    required String value,
  }) {
    return Container(
      margin: const EdgeInsets.only(bottom: 14),
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(24),
      ),
      child: Row(
        children: [
          Container(
            width: 50,
            height: 50,
            decoration: BoxDecoration(
              color: AppColors.primary.withValues(alpha: 0.10),
              borderRadius: BorderRadius.circular(16),
            ),
            child: Icon(
              icon,
              color: AppColors.primary,
            ),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: const TextStyle(
                    color: AppColors.textLight,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                const SizedBox(height: 6),
                Text(
                  value,
                  style: const TextStyle(
                    color: AppColors.textDark,
                    fontWeight: FontWeight.w800,
                    fontSize: 15,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget buildHeader() {
    final fullName = valueOf('full_name');
    final email = valueOf('email');

    return Container(
      padding: const EdgeInsets.all(28),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [
            AppColors.primary,
            AppColors.secondary,
          ],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(32),
      ),
      child: Column(
        children: [
          Container(
            width: 92,
            height: 92,
            decoration: BoxDecoration(
              color: Colors.white.withValues(alpha: 0.18),
              shape: BoxShape.circle,
            ),
            child: const Icon(
              Icons.person_rounded,
              size: 52,
              color: Colors.white,
            ),
          ),
          const SizedBox(height: 20),
          Text(
            fullName == 'Chưa cập nhật'
                ? 'Người dùng Chung Ví'
                : fullName,
            textAlign: TextAlign.center,
            style: const TextStyle(
              color: Colors.white,
              fontSize: 24,
              fontWeight: FontWeight.w900,
              letterSpacing: -0.6,
            ),
          ),
          const SizedBox(height: 10),
          Text(
            email,
            style: const TextStyle(
              color: Colors.white70,
              fontWeight: FontWeight.w600,
              fontSize: 15,
            ),
          ),
          const SizedBox(height: 22),
          SizedBox(
            height: 46,
            child: OutlinedButton.icon(
              onPressed: openEditProfile,
              icon: const Icon(Icons.edit_rounded),
              label: const Text('Chỉnh sửa hồ sơ'),
              style: OutlinedButton.styleFrom(
                foregroundColor: Colors.white,
                side: const BorderSide(
                  color: Colors.white70,
                ),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(18),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget buildLogoutButton() {
    return SizedBox(
      height: 58,
      child: ElevatedButton.icon(
        onPressed: logout,
        icon: const Icon(Icons.logout_rounded),
        label: const Text(
          'Đăng xuất',
          style: TextStyle(
            fontWeight: FontWeight.w800,
          ),
        ),
        style: ElevatedButton.styleFrom(
          backgroundColor: Colors.red,
          foregroundColor: Colors.white,
          elevation: 0,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(20),
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
        titleSpacing: 20,
        title: const Text('Cá nhân'),
      ),
      body: isLoading
          ? const Center(
              child: CircularProgressIndicator(),
            )
          : RefreshIndicator(
              onRefresh: loadProfile,
              child: ListView(
                padding: const EdgeInsets.all(20),
                children: [
                  buildHeader(),
                  const SizedBox(height: 28),
                  buildSectionTitle('Thông tin cá nhân'),
                  const SizedBox(height: 16),
                  buildInfoTile(
                    icon: Icons.badge_rounded,
                    title: 'Họ và tên',
                    value: valueOf('full_name'),
                  ),
                  buildInfoTile(
                    icon: Icons.email_rounded,
                    title: 'Email',
                    value: valueOf('email'),
                  ),
                  buildInfoTile(
                    icon: Icons.phone_rounded,
                    title: 'Số điện thoại',
                    value: valueOf('phone_number'),
                  ),
                  const SizedBox(height: 14),
                  buildSectionTitle('Tài khoản ngân hàng'),
                  const SizedBox(height: 16),
                  buildInfoTile(
                    icon: Icons.account_balance_rounded,
                    title: 'Ngân hàng',
                    value: valueOf('bank_name'),
                  ),
                  buildInfoTile(
                    icon: Icons.credit_card_rounded,
                    title: 'Số tài khoản',
                    value: valueOf('bank_account_number'),
                  ),
                  buildInfoTile(
                    icon: Icons.person_outline_rounded,
                    title: 'Chủ tài khoản',
                    value: valueOf('bank_account_holder'),
                  ),
                  const SizedBox(height: 28),
                  buildLogoutButton(),
                  const SizedBox(height: 120),
                ],
              ),
            ),
    );
  }
}