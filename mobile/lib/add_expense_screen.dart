import 'package:flutter/material.dart';

import 'app_theme.dart';
import 'models/household.dart';
import 'services/api_service.dart';

class AddExpenseScreen extends StatefulWidget {
  final Household household;

  const AddExpenseScreen({
    super.key,
    required this.household,
  });

  @override
  State<AddExpenseScreen> createState() => _AddExpenseScreenState();
}

class _AddExpenseScreenState extends State<AddExpenseScreen> {
  final titleController = TextEditingController();
  final amountController = TextEditingController();
  final noteController = TextEditingController();

  dynamic selectedPayer;
  final List<dynamic> selectedParticipants = [];

  bool isLoading = false;

  @override
  void initState() {
    super.initState();

    if (widget.household.members.isNotEmpty) {
      selectedPayer = widget.household.members.first;
      selectedParticipants.addAll(widget.household.members);
    }
  }

  @override
  void dispose() {
    titleController.dispose();
    amountController.dispose();
    noteController.dispose();
    super.dispose();
  }

  String getMemberEmail(dynamic member) {
    try {
      final value = member.email;
      if (value != null && value.toString().isNotEmpty) {
        return value.toString();
      }
    } catch (_) {}

    try {
      final value = member.userEmail;
      if (value != null && value.toString().isNotEmpty) {
        return value.toString();
      }
    } catch (_) {}

    try {
      final value = member.user_email;
      if (value != null && value.toString().isNotEmpty) {
        return value.toString();
      }
    } catch (_) {}

    return '';
  }

  String getMemberName(dynamic member) {
    try {
      final value = member.fullName;
      if (value != null && value.toString().isNotEmpty) {
        return value.toString();
      }
    } catch (_) {}

    final email = getMemberEmail(member);
    return email.isNotEmpty ? email : 'Thành viên';
  }

  int getMemberId(dynamic member) {
    try {
      final value = member.user;
      if (value is int) return value;
      return int.tryParse(value.toString()) ?? 0;
    } catch (_) {}

    try {
      final value = member.userId;
      if (value is int) return value;
      return int.tryParse(value.toString()) ?? 0;
    } catch (_) {}

    try {
      final value = member.id;
      if (value is int) return value;
      return int.tryParse(value.toString()) ?? 0;
    } catch (_) {}

    return 0;
  }

  double? parseAmount(String value) {
    final cleaned = value
        .replaceAll('.', '')
        .replaceAll(',', '')
        .replaceAll('đ', '')
        .trim();

    return double.tryParse(cleaned);
  }

  Future<void> createExpense() async {
    if (isLoading) return;
    
    final title = titleController.text.trim();
    final amount = parseAmount(amountController.text);

    if (amount == null || amount <= 0) {
      showMessage('Nhập số tiền hợp lệ');
      return;
    }

    if (title.isEmpty) {
      showMessage('Nhập tên khoản chi');
      return;
    }

    if (selectedPayer == null) {
      showMessage('Chọn người trả');
      return;
    }

    if (selectedParticipants.isEmpty) {
      showMessage('Chọn người tham gia');
      return;
    }

    final payerId = getMemberId(selectedPayer);
    final participantIds = selectedParticipants
        .map<int>((member) => getMemberId(member))
        .where((id) => id != 0)
        .toList();

    if (payerId == 0 || participantIds.isEmpty) {
      showMessage('Dữ liệu thành viên không hợp lệ');
      return;
    }

    try {
      setState(() => isLoading = true);

      await ApiService.createExpense(
        householdId: widget.household.id,
        title: title,
        amount: amount,
        payer: payerId,
        participants: participantIds,
        note: noteController.text.trim(),
      );

      if (!mounted) return;

      showMessage('Đã thêm khoản chi');
      Navigator.pop(context, true);
    } catch (e) {
      debugPrint(e.toString());
      showMessage('Không thể tạo khoản chi');
    } finally {
      if (mounted) {
        setState(() => isLoading = false);
      }
    }
  }

  void showMessage(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message)),
    );
  }

  Widget buildAmountCard() {
    return Container(
      padding: const EdgeInsets.all(22),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [
            AppColors.primary,
            AppColors.secondary,
          ],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(30),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Số tiền',
            style: TextStyle(
              color: Colors.white70,
              fontSize: 15,
              fontWeight: FontWeight.w700,
            ),
          ),
          const SizedBox(height: 14),
          Container(
            height: 72,
            padding: const EdgeInsets.symmetric(horizontal: 18),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(22),
            ),
            child: Row(
              children: [
                const Text(
                  '₫',
                  style: TextStyle(
                    color: AppColors.primary,
                    fontSize: 30,
                    fontWeight: FontWeight.w900,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: TextField(
                    controller: amountController,
                    keyboardType: TextInputType.number,
                    style: const TextStyle(
                      color: AppColors.textDark,
                      fontSize: 30,
                      fontWeight: FontWeight.w900,
                      letterSpacing: -0.7,
                    ),
                    decoration: const InputDecoration(
                      border: InputBorder.none,
                      enabledBorder: InputBorder.none,
                      focusedBorder: InputBorder.none,
                      filled: false,
                      hintText: '0',
                      hintStyle: TextStyle(
                        color: AppColors.textLight,
                        fontSize: 30,
                        fontWeight: FontWeight.w800,
                      ),
                      contentPadding: EdgeInsets.zero,
                    ),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget buildInput({
    required TextEditingController controller,
    required String hint,
    required IconData icon,
    int maxLines = 1,
  }) {
    final isMultiline = maxLines > 1;

    return TextField(
      controller: controller,
      maxLines: maxLines,
      minLines: maxLines,
      style: const TextStyle(
        fontSize: 15,
        fontWeight: FontWeight.w600,
        color: AppColors.textDark,
      ),
      decoration: InputDecoration(
        hintText: hint,
        prefixIcon: Padding(
          padding: EdgeInsets.only(
            left: 16,
            right: 12,
            top: isMultiline ? 18 : 0,
          ),
          child: Icon(
            icon,
            color: AppColors.textLight,
            size: 22,
          ),
        ),
        prefixIconConstraints: BoxConstraints(
          minWidth: 50,
          minHeight: isMultiline ? 56 : 52,
        ),
        contentPadding: EdgeInsets.symmetric(
          horizontal: 16,
          vertical: isMultiline ? 18 : 16,
        ),
      ),
    );
  }

  Widget buildSectionTitle(String title) {
    return Align(
      alignment: Alignment.centerLeft,
      child: Text(
        title,
        style: const TextStyle(
          fontSize: 19,
          fontWeight: FontWeight.w900,
          color: AppColors.textDark,
          letterSpacing: -0.4,
        ),
      ),
    );
  }

  Widget buildPayerSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        buildSectionTitle('Người trả'),
        const SizedBox(height: 14),
        ...widget.household.members.map(buildPayerTile),
      ],
    );
  }

  Widget buildPayerTile(dynamic member) {
    final isSelected = selectedPayer == member;
    final name = getMemberName(member);
    final email = getMemberEmail(member);
    final firstLetter = name.isNotEmpty ? name[0].toUpperCase() : '?';

    return GestureDetector(
      onTap: () {
        setState(() {
          selectedPayer = member;
        });
      },
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 180),
        margin: const EdgeInsets.only(bottom: 10),
        padding: const EdgeInsets.all(14),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(20),
          border: Border.all(
            color: isSelected ? AppColors.primary : AppColors.border,
            width: isSelected ? 1.4 : 1,
          ),
        ),
        child: Row(
          children: [
            CircleAvatar(
              radius: 20,
              backgroundColor: isSelected
                  ? AppColors.primary
                  : AppColors.primary.withValues(alpha: 0.12),
              child: Text(
                firstLetter,
                style: TextStyle(
                  color: isSelected ? Colors.white : AppColors.primary,
                  fontWeight: FontWeight.w900,
                ),
              ),
            ),
            const SizedBox(width: 14),
            Expanded(
              child: Text(
                email.isNotEmpty ? email : name,
                overflow: TextOverflow.ellipsis,
                style: const TextStyle(
                  color: AppColors.textDark,
                  fontWeight: FontWeight.w800,
                  fontSize: 15,
                ),
              ),
            ),
            Icon(
              isSelected
                  ? Icons.check_circle_rounded
                  : Icons.radio_button_unchecked_rounded,
              color: isSelected ? AppColors.primary : AppColors.textLight,
            ),
          ],
        ),
      ),
    );
  }

  Widget buildParticipantSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        buildSectionTitle('Người tham gia chia tiền'),
        const SizedBox(height: 14),
        ...widget.household.members.map(buildParticipantTile),
      ],
    );
  }

  Widget buildParticipantTile(dynamic member) {
    final isSelected = selectedParticipants.contains(member);
    final name = getMemberName(member);
    final email = getMemberEmail(member);
    final firstLetter = name.isNotEmpty ? name[0].toUpperCase() : '?';

    return GestureDetector(
      onTap: () {
        setState(() {
          if (isSelected) {
            selectedParticipants.remove(member);
          } else {
            selectedParticipants.add(member);
          }
        });
      },
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 180),
        margin: const EdgeInsets.only(bottom: 10),
        padding: const EdgeInsets.all(14),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(20),
          border: Border.all(
            color: isSelected ? AppColors.primary : AppColors.border,
            width: isSelected ? 1.4 : 1,
          ),
        ),
        child: Row(
          children: [
            CircleAvatar(
              radius: 20,
              backgroundColor: isSelected
                  ? AppColors.primary
                  : AppColors.primary.withValues(alpha: 0.12),
              child: Text(
                firstLetter,
                style: TextStyle(
                  color: isSelected ? Colors.white : AppColors.primary,
                  fontWeight: FontWeight.w900,
                ),
              ),
            ),
            const SizedBox(width: 14),
            Expanded(
              child: Text(
                email.isNotEmpty ? email : name,
                overflow: TextOverflow.ellipsis,
                style: const TextStyle(
                  color: AppColors.textDark,
                  fontWeight: FontWeight.w800,
                  fontSize: 15,
                ),
              ),
            ),
            Icon(
              isSelected
                  ? Icons.check_circle_rounded
                  : Icons.add_circle_outline_rounded,
              color: isSelected ? AppColors.primary : AppColors.textLight,
            ),
          ],
        ),
      ),
    );
  }

  Widget buildSaveButton() {
    return SizedBox(
      width: double.infinity,
      height: 58,
      child: ElevatedButton(
        onPressed: isLoading ? null : createExpense,
        child: isLoading
            ? const SizedBox(
                width: 22,
                height: 22,
                child: CircularProgressIndicator(
                  strokeWidth: 2.5,
                  color: Colors.white,
                ),
              )
            : const Text('Lưu khoản chi'),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        titleSpacing: 20,
        title: const Text('Thêm khoản chi'),
      ),
      body: SafeArea(
        child: Column(
          children: [
            Expanded(
              child: SingleChildScrollView(
                padding: const EdgeInsets.all(20),
                child: Column(
                  children: [
                    buildAmountCard(),
                    const SizedBox(height: 22),
                    buildInput(
                      controller: titleController,
                      hint: 'Tên khoản chi',
                      icon: Icons.receipt_long_rounded,
                    ),
                    const SizedBox(height: 16),
                    buildInput(
                      controller: noteController,
                      hint: 'Ghi chú',
                      icon: Icons.notes_rounded,
                      maxLines: 2,
                    ),
                    const SizedBox(height: 28),
                    buildPayerSection(),
                    const SizedBox(height: 28),
                    buildParticipantSection(),
                    const SizedBox(height: 24),
                  ],
                ),
              ),
            ),
            Container(
              padding: const EdgeInsets.fromLTRB(20, 12, 20, 20),
              decoration: BoxDecoration(
                color: AppColors.background,
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withValues(alpha: 0.04),
                    blurRadius: 18,
                    offset: const Offset(0, -6),
                  ),
                ],
              ),
              child: buildSaveButton(),
            ),
          ],
        ),
      ),
    );
  }
}