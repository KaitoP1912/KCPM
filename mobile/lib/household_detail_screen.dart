import 'package:flutter/material.dart';

import 'add_expense_screen.dart';
import 'app_theme.dart';
import 'models/debt.dart';
import 'models/expense.dart';
import 'models/household.dart';
import 'services/api_service.dart';
import 'package:url_launcher/url_launcher.dart';
import 'widgets/app_empty_state.dart';
import 'widgets/app_error_state.dart';
import 'widgets/app_loading_state.dart';
import 'package:flutter/services.dart';

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
  late Household household;

  bool isLoading = true;
  bool isAddingMember = false;
  bool isLeavingHousehold = false;
  String? errorMessage;

  List<Expense> expenses = [];
  List<Debt> debts = [];

  double totalExpense = 0;

  String currentUserEmail = '';

  final ScrollController scrollController =
      ScrollController();

  int expensePage = 1;
  bool hasMoreExpenses = true;
  bool isLoadingMoreExpenses = false;
  bool isExpensePageError = false;

  @override
  void initState() {
    super.initState();

    household = widget.household;

    scrollController.addListener(() {
      if (scrollController.position.pixels >=
          scrollController.position.maxScrollExtent - 300) {
        loadMoreExpenses();
      }
    });

    loadData();
  }

  @override
  void dispose() {
    scrollController.dispose();
    super.dispose();
  }

  bool get isCurrentUserOwner {
    return household.members.any(
      (member) =>
          member.role == 'owner' &&
          member.userEmail.trim().toLowerCase() ==
              currentUserEmail,
    );
  }

  Future<void> loadData() async {
    if (!mounted) return;

    setState(() {
      isLoading = true;
      errorMessage = null;
    });

    try {
      final savedEmail = await ApiService.getSavedEmail();

      if (savedEmail != null && savedEmail.isNotEmpty) {
        currentUserEmail =
            savedEmail.trim().toLowerCase();
      } else {
        final profile = await ApiService.getProfile();

        currentUserEmail = profile['email']
                ?.toString()
                .trim()
                .toLowerCase() ??
            '';
      }

      final householdData =
          await ApiService.getHouseholdDetail(
        household.id,
      );

      final freshHousehold =
          Household.fromJson(householdData);

      final expenseResponse =
          await ApiService.getHouseholdExpenses(
        household.id,
        page: 1,
      );

      final debtData =
          await ApiService.getHouseholdDebts(
        household.id,
      );

      final loadedExpenses = List<dynamic>.from(
        expenseResponse['results'],
      ).map<Expense>(
        (json) => Expense.fromJson(
          Map<String, dynamic>.from(json),
        ),
      ).toList();

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
        household = freshHousehold;

        expenses = loadedExpenses;
        debts = loadedDebts;
        totalExpense = total;

        expensePage = 1;
        hasMoreExpenses = expenseResponse['next'] != null;
        isLoadingMoreExpenses = false;
        isExpensePageError = false;

        isLoading = false;
        errorMessage = null;
      });
    } catch (e) {
      debugPrint(e.toString());

      if (!mounted) return;

      setState(() {
        errorMessage = 'Không thể tải dữ liệu nhóm';
        isLoading = false;
      });
    }
  }

  Future<void> refreshData() async {
    await loadData();
  }

  Future<void> loadMoreExpenses() async {
    if (isLoadingMoreExpenses ||
        !hasMoreExpenses ||
        isLoading ||
        isExpensePageError) {
      return;
    }

    setState(() {
      isLoadingMoreExpenses = true;
      isExpensePageError = false;
    });

    try {
      final nextPage = expensePage + 1;

      final response =
          await ApiService.getHouseholdExpenses(
        household.id,
        page: nextPage,
      );

      final newExpenses = List<dynamic>.from(
        response['results'],
      ).map<Expense>(
        (json) => Expense.fromJson(
          Map<String, dynamic>.from(json),
        ),
      ).toList();

      double addedTotal = 0;

      for (final expense in newExpenses) {
        addedTotal += expense.amount;
      }

      if (!mounted) return;

      setState(() {
        expensePage = nextPage;
        expenses.addAll(newExpenses);
        totalExpense += addedTotal;
        hasMoreExpenses = response['next'] != null;
        isLoadingMoreExpenses = false;
      });
    } catch (e) {
      debugPrint(e.toString());

      if (!mounted) return;

      setState(() {
        isLoadingMoreExpenses = false;
        isExpensePageError = true;
      });
    }
  }

  Future<void> openAddExpenseScreen() async {
    final result = await Navigator.push(
      context,
      MaterialPageRoute(
        builder: (_) => AddExpenseScreen(
          household: household,
        ),
      ),
    );

    if (result == true) {
      await loadData();
    }
  }

  Future<void> showAddMemberDialog() async {
    if (!isCurrentUserOwner) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Chỉ chủ nhóm mới được thêm thành viên'),
        ),
      );
      return;
    }

    final controller = TextEditingController();

    await showDialog(
      context: context,
      barrierDismissible: !isAddingMember,
      builder: (dialogContext) {
        return StatefulBuilder(
          builder: (dialogContext, setDialogState) {
            Future<void> submit() async {
              if (isAddingMember) return;

              final email = controller.text.trim().toLowerCase();

              if (email.isEmpty) {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(
                    content: Text('Nhập email thành viên'),
                  ),
                );
                return;
              }

              if (!email.contains('@')) {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(
                    content: Text('Email không hợp lệ'),
                  ),
                );
                return;
              }

              setDialogState(() => isAddingMember = true);

              try {
                await ApiService.addMemberToHousehold(
                  householdId: household.id,
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
              } finally {
                if (mounted) {
                  setDialogState(() => isAddingMember = false);
                }
              }
            }

            return AlertDialog(
              title: const Text('Thêm thành viên'),
              content: TextField(
                controller: controller,
                enabled: !isAddingMember,
                keyboardType: TextInputType.emailAddress,
                textInputAction: TextInputAction.done,
                onSubmitted: (_) => submit(),
                decoration: const InputDecoration(
                  hintText: 'Nhập email...',
                ),
              ),
              actions: [
                TextButton(
                  onPressed: isAddingMember
                      ? null
                      : () {
                          Navigator.pop(dialogContext);
                        },
                  child: const Text('Hủy'),
                ),
                ElevatedButton(
                  onPressed: isAddingMember ? null : submit,
                  child: isAddingMember
                      ? const SizedBox(
                          width: 18,
                          height: 18,
                          child: CircularProgressIndicator(
                            strokeWidth: 2.2,
                            color: Colors.white,
                          ),
                        )
                      : const Text('Thêm'),
                ),
              ],
            );
          },
        );
      },
    );

    controller.dispose();
  }

  Future<void> confirmLeaveHousehold() async {
    if (isLeavingHousehold) return;

    final confirmed = await showDialog<bool>(
      context: context,
      builder: (dialogContext) {
        return AlertDialog(
          title: const Text('Rời nhóm?'),
          content: const Text(
            'Bạn sẽ không còn xem được khoản chi và công nợ của nhóm này.',
          ),
          actions: [
            TextButton(
              onPressed: () {
                Navigator.pop(dialogContext, false);
              },
              child: const Text('Hủy'),
            ),
            ElevatedButton(
              onPressed: () {
                Navigator.pop(dialogContext, true);
              },
              child: const Text('Rời nhóm'),
            ),
          ],
        );
      },
    );

    if (confirmed != true) return;

    setState(() {
      isLeavingHousehold = true;
    });

    try {
      await ApiService.leaveHousehold(household.id);

      if (!mounted) return;

      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Bạn đã rời nhóm'),
        ),
      );

      Navigator.pop(context, true);
    } catch (e) {
      if (!mounted) return;

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(e.toString()),
        ),
      );
    } finally {
        if (mounted) {
          setState(() {
            isLeavingHousehold = false;
          });
        }
      }
    }

  String formatMoney(double amount) {
    return amount.toStringAsFixed(0).replaceAllMapped(
          RegExp(r'\B(?=(\d{3})+(?!\d))'),
          (match) => '.',
        );
  }

  String displayUserName({
    required String name,
    required String email,
  }) {
    final normalizedEmail = email.trim().toLowerCase();

    if (normalizedEmail.isNotEmpty &&
        normalizedEmail == currentUserEmail) {
      return 'Bạn';
    }

    if (name.trim().isNotEmpty) {
      return name;
    }

    return email;
  }

  Widget buildAvatar({
    required String imageUrl,
    required String name,
    double radius = 24,
  }) {
    if (imageUrl.isNotEmpty) {
      return CircleAvatar(
        radius: radius,
        backgroundImage: NetworkImage(imageUrl),
        backgroundColor: Colors.grey.shade200,
      );
    }

    return CircleAvatar(
      radius: radius,
      backgroundColor: AppColors.primary,
      child: Text(
        name.isNotEmpty
            ? name[0].toUpperCase()
            : '?',
        style: TextStyle(
          color: Colors.white,
          fontWeight: FontWeight.w800,
          fontSize: radius * 0.8,
        ),
      ),
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
                    Row(
                      crossAxisAlignment:
                          CrossAxisAlignment.start,
                      children: [
                        Expanded(
                          child: Text(
                            household.name,
                            style: const TextStyle(
                              color: Colors.white,
                              fontSize: 26,
                              fontWeight: FontWeight.w900,
                              letterSpacing: -0.7,
                            ),
                          ),
                        ),

                        const SizedBox(width: 12),

                        InkWell(
                          borderRadius:
                              BorderRadius.circular(999),
                          onTap: () async {
                            await Clipboard.setData(
                              ClipboardData(
                                text:
                                    household.inviteCode,
                              ),
                            );

                            if (!mounted) return;

                            ScaffoldMessenger.of(context)
                                .showSnackBar(
                              const SnackBar(
                                content: Text(
                                  'Đã copy mã mời',
                                ),
                              ),
                            );
                          },
                          child: Container(
                            padding:
                                const EdgeInsets.symmetric(
                              horizontal: 12,
                              vertical: 8,
                            ),
                            decoration: BoxDecoration(
                              color: Colors.white.withValues(
                                alpha: 0.16,
                              ),
                              borderRadius:
                                  BorderRadius.circular(999),
                              border: Border.all(
                                color: Colors.white.withValues(
                                  alpha: 0.12,
                                ),
                              ),
                            ),
                            child: Row(
                              mainAxisSize:
                                  MainAxisSize.min,
                              children: [
                                const Icon(
                                  Icons.key_rounded,
                                  color: Colors.white,
                                  size: 14,
                                ),

                                const SizedBox(width: 6),

                                Text(
                                  household.inviteCode,
                                  style: const TextStyle(
                                    color: Colors.white,
                                    fontSize: 13,
                                    fontWeight:
                                        FontWeight.w800,
                                    letterSpacing: 0.5,
                                  ),
                                ),

                                const SizedBox(width: 6),

                                const Icon(
                                  Icons.copy_rounded,
                                  color: Colors.white70,
                                  size: 14,
                                ),
                              ],
                            ),
                          ),
                        ),
                      ],
                    ),

                    Text(
                      household.description.isEmpty
                          ? 'Nhóm chia tiền'
                          : household.description,
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
                label: '${household.members.length} thành viên',
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
    final members = household.members;

    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(28),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Text(
                'Thành viên',
                style: TextStyle(
                  fontSize: 20,
                  fontWeight: FontWeight.w900,
                  color: AppColors.textDark,
                ),
              ),
              const Spacer(),
              TextButton(
                onPressed: () {},
                child: const Text('View all'),
              ),
            ],
          ),
          const SizedBox(height: 18),
          SizedBox(
            height: 88,
            child: ListView.separated(
              scrollDirection: Axis.horizontal,
              itemCount: members.length,
              separatorBuilder: (_, _) =>
                  const SizedBox(width: 16),
              itemBuilder: (_, index) {
                final member = members[index];

                return SizedBox(
                  width: 64,
                  child: Column(
                    children: [
                      buildAvatar(
                        imageUrl: member.userAvatar,
                        name: member.displayName,
                        radius: 22,
                      ),
                      const SizedBox(height: 6),
                      Text(
                        member.displayName,
                        maxLines: 2,
                        overflow: TextOverflow.ellipsis,
                        textAlign: TextAlign.center,
                        style: const TextStyle(
                          fontSize: 11,
                          fontWeight: FontWeight.w700,
                          color: AppColors.textDark,
                        ),
                      ),
                    ],
                  ),
                );
              },
            ),
          ),
        ],
      ),
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
    final previewDebts = debts;

    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(28),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Text(
                'Công nợ',
                style: TextStyle(
                  fontSize: 20,
                  fontWeight: FontWeight.w900,
                  color: AppColors.textDark,
                ),
              ),
              const Spacer(),
              TextButton(
                onPressed: () {},
                child: const Text('View all'),
              ),
            ],
          ),
          const SizedBox(height: 16),
          if (previewDebts.isEmpty)
            buildEmptyCard(
              icon: Icons.check_circle_outline,
              title: 'Không có công nợ',
            )
          else
            SizedBox(
              height: debts.length == 1
                ? 116.0
                : debts.length == 2
                    ? 224.0
                    : 312.0,
              child: ListView.builder(
                physics: debts.length >= 4
                  ? const ClampingScrollPhysics()
                  : const NeverScrollableScrollPhysics(),
                padding: EdgeInsets.zero,
                itemCount: debts.length,
                itemBuilder: (context, index) {
                  return buildCompactDebtCard(
                    debts[index],
                  );
                },
              ),
            ),
          ]
      ),
    );
  }

  Widget buildCompactDebtCard(Debt debt) {
    final fromName = displayUserName(
      name: debt.fromUserName,
      email: debt.fromUserEmail,
    );

    final toName = displayUserName(
      name: debt.toUserName,
      email: debt.toUserEmail,
    );

    return GestureDetector(
      onTap: () => openTransferQR(debt),
      child: Container(
        margin: const EdgeInsets.only(bottom: 12),
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: AppColors.background,
          borderRadius: BorderRadius.circular(22),
        ),
        child: Row(
          children: [
            buildAvatar(
              imageUrl: debt.fromUserAvatar,
              name: fromName,
              radius: 24,
            ),
            const SizedBox(width: 14),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    fromName,
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: const TextStyle(
                      fontWeight: FontWeight.w900,
                      color: AppColors.textDark,
                      fontSize: 15,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    'Cần trả ${formatMoney(debt.amount)}đ',
                    style: const TextStyle(
                      color: AppColors.warning,
                      fontWeight: FontWeight.w900,
                      fontSize: 14,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Row(
                    children: [
                      const Icon(
                        Icons.arrow_downward_rounded,
                        size: 16,
                        color: AppColors.textLight,
                      ),
                      const SizedBox(width: 6),
                      Expanded(
                        child: Text(
                          'Người nhận: $toName',
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                          style: const TextStyle(
                            color: AppColors.textLight,
                            fontWeight: FontWeight.w700,
                            fontSize: 12,
                          ),
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
            const SizedBox(width: 12),
            buildAvatar(
              imageUrl: debt.toUserAvatar,
              name: toName,
              radius: 24,
            ),
          ],
        ),
      ),
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
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(28),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Text(
                'Khoản chi gần đây',
                style: TextStyle(
                  fontSize: 20,
                  fontWeight: FontWeight.w900,
                  color: AppColors.textDark,
                ),
              ),
              const Spacer(),
              TextButton(
                onPressed: () {},
                child: const Text('View all'),
              ),
            ],
          ),
          const SizedBox(height: 16),

          if (expenses.isEmpty)
            buildEmptyCard(
              icon: Icons.receipt_long,
              title: 'Chưa có khoản chi',
            )
          else
            Column(
              children: [
                ...expenses.map(
                  buildCompactExpenseCard,
                ),

                if (isLoadingMoreExpenses)
                  const Padding(
                    padding: EdgeInsets.symmetric(vertical: 18),
                    child: Center(
                      child: CircularProgressIndicator(),
                    ),
                  ),

                if (isExpensePageError)
                  Padding(
                    padding: const EdgeInsets.only(top: 12),
                    child: Column(
                      children: [
                        const Text(
                          'Không tải được thêm khoản chi',
                          style: TextStyle(
                            color: AppColors.textLight,
                            fontWeight: FontWeight.w700,
                          ),
                        ),
                        const SizedBox(height: 8),
                        OutlinedButton(
                          onPressed: () {
                            setState(() {
                              isExpensePageError = false;
                            });

                            loadMoreExpenses();
                          },
                          child: const Text('Thử lại'),
                        ),
                      ],
                    ),
                  ),

                if (!hasMoreExpenses &&
                    expenses.isNotEmpty &&
                    !isLoadingMoreExpenses)
                  const Padding(
                    padding: EdgeInsets.symmetric(vertical: 12),
                    child: Text(
                      'Đã tải hết khoản chi',
                      style: TextStyle(
                        color: AppColors.textLight,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ),
              ],
            ),
        ],
      ),
    );
  }

  Widget buildCompactExpenseCard(
    Expense expense,
  ) {
    return Container(
      margin: const EdgeInsets.only(bottom: 20),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppColors.background,
        borderRadius: BorderRadius.circular(22),
      ),
      child: Row(
        children: [
          buildAvatar(
            imageUrl: expense.payerAvatar,
            name: displayUserName(
              name: expense.payerName,
              email: expense.payerEmail,
            ),
            radius: 24,
          ),
          const SizedBox(width: 14),
          Expanded(
            child: Column(
              crossAxisAlignment:
                  CrossAxisAlignment.start,
              children: [
                Text(
                  expense.title,
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  style: const TextStyle(
                    fontWeight: FontWeight.w800,
                    color: AppColors.textDark,
                  ),
                ),
                const SizedBox(height: 6),
                Text(
                  displayUserName(
                    name: expense.payerName,
                    email: expense.payerEmail,
                  ),
                  style: const TextStyle(
                    color: AppColors.textLight,
                    fontWeight: FontWeight.w600,
                    fontSize: 13,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  expense.expenseDate,
                  style: const TextStyle(
                    color: AppColors.textLight,
                    fontSize: 12,
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(width: 12),
          Text(
            '${formatMoney(expense.amount)}đ',
            style: const TextStyle(
              fontWeight: FontWeight.w900,
              color: AppColors.primary,
            ),
          ),
        ],
      ),
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
    if (isLoading) {
      return const Scaffold(
        backgroundColor: AppColors.background,
        body: AppLoadingState(
          message: 'Đang tải dữ liệu nhóm...',
        ),
      );
    }

    if (errorMessage != null) {
      return Scaffold(
        backgroundColor: AppColors.background,
        body: AppErrorState(
          message: errorMessage!,
          onRetry: loadData,
        ),
      );
    }

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        titleSpacing: 20,
        title: Text(household.name),
        actions: [
          PopupMenuButton<String>(
            icon: const Icon(Icons.more_vert_rounded),
            onSelected: (value) {
              if (value == 'add_member') {
                showAddMemberDialog();
              }

              if (value == 'leave') {
                confirmLeaveHousehold();
              }
            },
            itemBuilder: (context) => [
              const PopupMenuItem(
                value: 'add_member',
                child: Text('Thêm thành viên'),
              ),
              PopupMenuItem(
                value: 'leave',
                enabled: !isLeavingHousehold,
                child: Text(
                  isLeavingHousehold ? 'Đang rời nhóm...' : 'Rời nhóm',
                ),
              ),
            ],
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
      body: RefreshIndicator(
        onRefresh: refreshData,
        child: ListView(
          controller: scrollController,
          physics:
              const AlwaysScrollableScrollPhysics(),
          padding: const EdgeInsets.all(20),
          children: [
            buildHeroCard(),
            const SizedBox(height: 30),
            buildMembersSection(),
            const SizedBox(height: 30),
            buildDebtSection(),
            const SizedBox(height: 30),
            if (expenses.isEmpty)
              SizedBox(
                height:
                    MediaQuery.of(context).size.height *
                    0.42,
                child: AppEmptyState(
                  icon: Icons.receipt_long_rounded,
                  title: 'Chưa có khoản chi',
                  message:
                      'Thêm khoản chi đầu tiên để Chung Ví tự động tính toán công nợ cho nhóm.',
                  buttonText: 'Thêm khoản chi',
                  onPressed: openAddExpenseScreen,
                ),
              )
            else
              buildExpenseSection(),
            const SizedBox(height: 120),
          ],
        ),
      ),
    );
  }
}