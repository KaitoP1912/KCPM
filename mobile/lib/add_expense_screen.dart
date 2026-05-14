import 'package:flutter/material.dart';

import 'app_theme.dart';
import 'models/household.dart';
import 'models/member.dart';
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

  int? selectedPayer;
  final Set<int> selectedParticipants = {};
  bool isLoading = false;

  @override
  void initState() {
    super.initState();

    if (widget.household.members.isNotEmpty) {
      selectedPayer = widget.household.members.first.user;
      selectedParticipants.addAll(
        widget.household.members.map((member) => member.user),
      );
    }
  }

  Future<void> submitExpense() async {
    final title = titleController.text.trim();
    final amount = double.tryParse(
      amountController.text.trim().replaceAll(',', ''),
    );

    if (title.isEmpty || amount == null || amount <= 0) {
      showMessage('Vui lòng nhập tên khoản chi và số tiền hợp lệ');
      return;
    }

    if (selectedPayer == null) {
      showMessage('Vui lòng chọn người trả tiền');
      return;
    }

    if (selectedParticipants.isEmpty) {
      showMessage('Vui lòng chọn ít nhất 1 người tham gia');
      return;
    }

    try {
      setState(() => isLoading = true);

      await ApiService.createExpense(
        householdId: widget.household.id,
        title: title,
        amount: amount,
        payer: selectedPayer!,
        participants: selectedParticipants.toList(),
        note: noteController.text.trim(),
      );

      if (!mounted) return;
      Navigator.pop(context, true);
    } catch (e) {
      showMessage('Thêm khoản chi thất bại. Kiểm tra lại API serializer.');
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

  String memberName(HouseholdMember member) {
    if (member.fullName.trim().isNotEmpty) return member.fullName;
    return member.email;
  }

  @override
  Widget build(BuildContext context) {
    final members = widget.household.members;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Thêm khoản chi'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Column(
          children: [
            TextField(
              controller: titleController,
              decoration: const InputDecoration(
                hintText: 'Tên khoản chi',
                prefixIcon: Icon(Icons.receipt_long_outlined),
              ),
            ),
            const SizedBox(height: 14),
            TextField(
              controller: amountController,
              keyboardType: TextInputType.number,
              decoration: const InputDecoration(
                hintText: 'Số tiền',
                prefixIcon: Icon(Icons.payments_outlined),
              ),
            ),
            const SizedBox(height: 14),
            DropdownButtonFormField<int>(
              value: selectedPayer,
              decoration: const InputDecoration(
                hintText: 'Người trả tiền',
                prefixIcon: Icon(Icons.person_outline),
              ),
              items: members.map((member) {
                return DropdownMenuItem<int>(
                  value: member.user,
                  child: Text(memberName(member)),
                );
              }).toList(),
              onChanged: (value) {
                setState(() {
                  selectedPayer = value;
                });
              },
            ),
            const SizedBox(height: 22),
            _SectionCard(
              title: 'Người tham gia',
              child: members.isEmpty
                  ? const Text('Nhóm chưa có thành viên')
                  : Column(
                      children: members.map((member) {
                        final checked =
                            selectedParticipants.contains(member.user);

                        return CheckboxListTile(
                          value: checked,
                          contentPadding: EdgeInsets.zero,
                          activeColor: AppColors.primary,
                          title: Text(memberName(member)),
                          subtitle: Text(member.role),
                          onChanged: (value) {
                            setState(() {
                              if (value == true) {
                                selectedParticipants.add(member.user);
                              } else {
                                selectedParticipants.remove(member.user);
                              }
                            });
                          },
                        );
                      }).toList(),
                    ),
            ),
            const SizedBox(height: 14),
            TextField(
              controller: noteController,
              maxLines: 3,
              decoration: const InputDecoration(
                hintText: 'Ghi chú',
                prefixIcon: Icon(Icons.notes_outlined),
              ),
            ),
            const SizedBox(height: 24),
            SizedBox(
              width: double.infinity,
              height: 56,
              child: ElevatedButton(
                onPressed: isLoading ? null : submitExpense,
                child: isLoading
                    ? const CircularProgressIndicator(color: Colors.white)
                    : const Text(
                        'Lưu khoản chi',
                        style: TextStyle(
                          fontWeight: FontWeight.w700,
                        ),
                      ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _SectionCard extends StatelessWidget {
  final String title;
  final Widget child;

  const _SectionCard({
    required this.title,
    required this.child,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(22),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: const TextStyle(
              fontWeight: FontWeight.w800,
              fontSize: 16,
            ),
          ),
          const SizedBox(height: 10),
          child,
        ],
      ),
    );
  }
}