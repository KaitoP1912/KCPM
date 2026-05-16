import 'package:flutter/material.dart';

import 'activity_screen.dart';
import 'add_expense_screen.dart';
import 'app_theme.dart';
import 'models/debt.dart';
import 'models/expense.dart';
import 'models/household.dart';
import 'services/api_service.dart';
import 'package:url_launcher/url_launcher.dart';

class HouseholdDetailScreen extends StatefulWidget {
  final Household household;

  const HouseholdDetailScreen({
    super.key,
    required this.household,
  });

  @override
  State<HouseholdDetailScreen> createState() =>
      _HouseholdDetailScreenState();
}

class _HouseholdDetailScreenState extends State<HouseholdDetailScreen> {
  bool isLoading = true;

  List<Expense> expenses = [];
  List<Debt> debts = [];

  double totalExpense = 0;

  @override
  void initState() {
    super.initState();
    loadData();
  }

  Future<void> loadData() async {
    setState(() {
      isLoading = true;
    });

    try {
      final expenseData = await ApiService.getHouseholdExpenses(
        widget.household.id,
      );

      final debtData = await ApiService.getHouseholdDebts(
        widget.household.id,
      );

      final loadedExpenses = expenseData
          .map<Expense>(
            (json) => Expense.fromJson(
              Map<String, dynamic>.from(json),
            ),
          )
          .toList();

      final loadedDebts = debtData
          .map<Debt>(
            (json) => Debt.fromJson(
              Map<String, dynamic>.from(json),
            ),
          )
          .toList();

      double total = 0;

      for (final expense in loadedExpenses) {
        total += expense.amount;
      }

      if (!mounted) return;

      setState(() {
        expenses = loadedExpenses;
        debts = loadedDebts;
        totalExpense = total;
        isLoading = false;
      });
    } catch (e) {
      debugPrint(e.toString());

      if (!mounted) return;

      setState(() {
        isLoading = false;
      });

      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Không thể tải dữ liệu nhóm'),
        ),
      );
    }
  }

  Future<void> openAddExpenseScreen() async {
    final result = await Navigator.push(
      context,
      MaterialPageRoute(
        builder: (_) => AddExpenseScreen(
          household: widget.household,
        ),
      ),
    );

    if (result == true) {
      await loadData();
    }
  }

  Future<void> showAddMemberDialog() async {
    final controller = TextEditingController();

    await showDialog(
      context: context,
      builder: (dialogContext) {
        return AlertDialog(
          title: const Text('Thêm thành viên'),
          content: TextField(
            controller: controller,
            keyboardType: TextInputType.emailAddress,
            decoration: const InputDecoration(
              hintText: 'Nhập email...',
            ),
          ),
          actions: [
            TextButton(
              onPressed: () {
                Navigator.pop(dialogContext);
              },
              child: const Text('Hủy'),
            ),
            ElevatedButton(
              onPressed: () async {
                final email = controller.text.trim();

                if (email.isEmpty) {
                  return;
                }

                try {
                  await ApiService.addMemberToHousehold(
                    householdId: widget.household.id,
                    email: email,
                  );

                  if (!mounted || !dialogContext.mounted) return;

                  Navigator.pop(dialogContext);

                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(
                      content: Text('Đã thêm thành viên'),
                    ),
                  );

                  await loadData();
                } catch (e) {
                  if (!mounted) return;

                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(
                      content: Text(e.toString()),
                    ),
                  );
                }
              },
              child: const Text('Thêm'),
            ),
          ],
        );
      },
    );

    controller.dispose();
  }

  String formatMoney(double amount) {
    return amount.toStringAsFixed(0).replaceAllMapped(
          RegExp(r'\B(?=(\d{3})+(?!\d))'),
          (match) => '.',
        );
  }

  Future<void> openTransferQR(Debt debt) async {
    if (debt.bankName.isEmpty ||
        debt.bankAccountNumber.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text(
            'Người nhận chưa cập nhật tài khoản ngân hàng',
          ),
        ),
      );

      return;
    }

    final amount = debt.amount.toInt();

    final encodedMessage = Uri.encodeComponent(
      'Thanh toan Chung Vi',
    );

    final encodedAccountName = Uri.encodeComponent(
      debt.bankAccountHolder,
    );

    final url =
        'https://img.vietqr.io/image/'
        '${debt.bankName}-${debt.bankAccountNumber}-compact2.png'
        '?amount=$amount'
        '&addInfo=$encodedMessage'
        '&accountName=$encodedAccountName';

    final uri = Uri.parse(url);

    try {
      final launched = await launchUrl(
        uri,
        mode: LaunchMode.externalApplication,
      );

      if (!launched && mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text(
              'Không thể mở QR chuyển khoản',
            ),
          ),
        );
      }
    } catch (e) {
      if (!mounted) return;

      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text(
            'Đã xảy ra lỗi khi mở QR',
          ),
        ),
      );
    }
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

    try {
      final value = member.userFullName;
      if (value != null && value.toString().isNotEmpty) {
        return value.toString();
      }
    } catch (_) {}

    final email = getMemberEmail(member);

    if (email.isNotEmpty) {
      return email;
    }

    return 'Thành viên';
  }

  Widget buildHeroCard() {
    return Container(
      padding: const EdgeInsets.all(24),
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
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                width: 58,
                height: 58,
                decoration: BoxDecoration(
                  color: Colors.white.withValues(alpha: 0.16),
                  borderRadius: BorderRadius.circular(18),
                ),
                child: const Icon(
                  Icons.groups_rounded,
                  color: Colors.white,
                  size: 30,
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      widget.household.name,
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 26,
                        fontWeight: FontWeight.w900,
                        letterSpacing: -0.7,
                      ),
                    ),
                    const SizedBox(height: 6),
                    Text(
                      widget.household.description.isEmpty
                          ? 'Nhóm chia tiền'
                          : widget.household.description,
                      style: const TextStyle(
                        color: Colors.white70,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 30),
          const Text(
            'Tổng chi tiêu',
            style: TextStyle(
              color: Colors.white70,
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: 10),
          Text(
            '${formatMoney(totalExpense)}đ',
            style: const TextStyle(
              color: Colors.white,
              fontSize: 36,
              fontWeight: FontWeight.w900,
              letterSpacing: -1,
            ),
          ),
          const SizedBox(height: 22),
          Row(
            children: [
              buildMiniInfo(
                icon: Icons.receipt_long,
                label: '${expenses.length} khoản chi',
              ),
              const SizedBox(width: 12),
              buildMiniInfo(
                icon: Icons.people_alt_rounded,
                label: '${widget.household.members.length} thành viên',
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget buildMiniInfo({
    required IconData icon,
    required String label,
  }) {
    return Container(
      padding: const EdgeInsets.symmetric(
        horizontal: 14,
        vertical: 10,
      ),
      decoration: BoxDecoration(
        color: Colors.white.withValues(alpha: 0.14),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Row(
        children: [
          Icon(
            icon,
            color: Colors.white,
            size: 18,
          ),
          const SizedBox(width: 8),
          Text(
            label,
            style: const TextStyle(
              color: Colors.white,
              fontWeight: FontWeight.w700,
            ),
          ),
        ],
      ),
    );
  }

  Widget buildMembersSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Thành viên',
          style: TextStyle(
            fontSize: 20,
            fontWeight: FontWeight.w900,
            color: AppColors.textDark,
            letterSpacing: -0.4,
          ),
        ),
        const SizedBox(height: 16),
        if (widget.household.members.isEmpty)
          buildEmptyCard(
            icon: Icons.people_outline_rounded,
            title: 'Chưa có thành viên',
          )
        else
          Wrap(
            spacing: 12,
            runSpacing: 12,
            children: widget.household.members
                .map(
                  (member) => buildMemberChip(member),
                )
                .toList(),
          ),
      ],
    );
  }

  Widget buildMemberChip(dynamic member) {
    final name = getMemberName(member);
    final email = getMemberEmail(member);

    final firstLetter = name.isNotEmpty ? name[0].toUpperCase() : '?';

    return Container(
      padding: const EdgeInsets.symmetric(
        horizontal: 14,
        vertical: 12,
      ),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(18),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          CircleAvatar(
            radius: 16,
            backgroundColor: AppColors.primary,
            child: Text(
              firstLetter,
              style: const TextStyle(
                color: Colors.white,
                fontWeight: FontWeight.w800,
              ),
            ),
          ),
          const SizedBox(width: 10),
          ConstrainedBox(
            constraints: const BoxConstraints(
              maxWidth: 210,
            ),
            child: Text(
              email.isNotEmpty ? email : name,
              overflow: TextOverflow.ellipsis,
              style: const TextStyle(
                fontWeight: FontWeight.w700,
                color: AppColors.textDark,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget buildDebtSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Công nợ',
          style: TextStyle(
            fontSize: 20,
            fontWeight: FontWeight.w900,
            color: AppColors.textDark,
            letterSpacing: -0.4,
          ),
        ),
        const SizedBox(height: 16),
        if (debts.isEmpty)
          buildEmptyCard(
            icon: Icons.check_circle_outline,
            title: 'Không có công nợ',
          )
        else
          ...debts.map(buildDebtCard),
      ],
    );
  }

  Widget buildDebtCard(Debt debt) {
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
            width: 52,
            height: 52,
            decoration: BoxDecoration(
              color: AppColors.warning.withValues(alpha: 0.12),
              borderRadius: BorderRadius.circular(16),
            ),
            child: const Icon(
              Icons.sync_alt_rounded,
              color: AppColors.warning,
            ),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  '${debt.fromUserEmail} → ${debt.toUserEmail}',
                  style: const TextStyle(
                    fontWeight: FontWeight.w800,
                    fontSize: 15,
                    color: AppColors.textDark,
                  ),
                ),
                const SizedBox(height: 6),
                Text(
                  '${formatMoney(debt.amount)}đ',
                  style: const TextStyle(
                    color: AppColors.warning,
                    fontWeight: FontWeight.w800,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget buildExpenseSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Khoản chi',
          style: TextStyle(
            fontSize: 20,
            fontWeight: FontWeight.w900,
            color: AppColors.textDark,
            letterSpacing: -0.4,
          ),
        ),
        const SizedBox(height: 16),
        if (expenses.isEmpty)
          buildEmptyCard(
            icon: Icons.receipt_long,
            title: 'Chưa có khoản chi',
          )
        else
          ...expenses.map(buildExpenseCard),
      ],
    );
  }

  Widget buildExpenseCard(Expense expense) {
    return Container(
      margin: const EdgeInsets.only(bottom: 14),
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(24),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.02),
            blurRadius: 20,
            offset: const Offset(0, 8),
          ),
        ],
      ),
      child: Row(
        children: [
          Container(
            width: 56,
            height: 56,
            decoration: BoxDecoration(
              gradient: const LinearGradient(
                colors: [
                  AppColors.primary,
                  AppColors.secondary,
                ],
              ),
              borderRadius: BorderRadius.circular(18),
            ),
            child: const Icon(
              Icons.payments_rounded,
              color: Colors.white,
            ),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  expense.title,
                  style: const TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.w800,
                    color: AppColors.textDark,
                  ),
                ),
                const SizedBox(height: 6),
                Text(
                  expense.payerEmail.isEmpty
                      ? 'Người trả đang cập nhật'
                      : expense.payerEmail,
                  style: const TextStyle(
                    color: AppColors.textLight,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(width: 12),
          Text(
            '${formatMoney(expense.amount)}đ',
            style: const TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.w900,
              color: AppColors.primary,
            ),
          ),
        ],
      ),
    );
  }

  Widget buildEmptyCard({
    required IconData icon,
    required String title,
  }) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(28),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(26),
      ),
      child: Column(
        children: [
          Icon(
            icon,
            size: 46,
            color: AppColors.textLight,
          ),
          const SizedBox(height: 16),
          Text(
            title,
            style: const TextStyle(
              color: AppColors.textDark,
              fontWeight: FontWeight.w800,
              fontSize: 16,
            ),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        titleSpacing: 20,
        title: Text(widget.household.name),
        actions: [
          IconButton(
            onPressed: showAddMemberDialog,
            icon: const Icon(
              Icons.person_add_alt_1_rounded,
            ),
          ),
          const SizedBox(width: 8),
          IconButton(
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (_) => ActivityScreen(
                    householdId: widget.household.id,
                  ),
                ),
              );
            },
            icon: const Icon(Icons.history_rounded),
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton.extended(
        elevation: 0,
        backgroundColor: AppColors.primary,
        onPressed: openAddExpenseScreen,
        icon: const Icon(
          Icons.add_rounded,
          color: Colors.white,
        ),
        label: const Text(
          'Thêm chi',
          style: TextStyle(
            color: Colors.white,
            fontWeight: FontWeight.w800,
          ),
        ),
      ),
      body: isLoading
          ? const Center(
              child: CircularProgressIndicator(),
            )
          : RefreshIndicator(
              onRefresh: loadData,
              child: ListView(
                padding: const EdgeInsets.all(20),
                children: [
                  buildHeroCard(),
                  const SizedBox(height: 30),
                  buildMembersSection(),
                  const SizedBox(height: 30),
                  buildDebtSection(),
                  const SizedBox(height: 30),
                  buildExpenseSection(),
                  const SizedBox(height: 120),
                ],
              ),
            ),
    );
  }
}