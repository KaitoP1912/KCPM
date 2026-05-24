import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import 'app_theme.dart';
import 'models/debt.dart';
import 'models/household.dart';
import 'services/api_service.dart';
import 'widgets/app_empty_state.dart';
import 'widgets/app_error_state.dart';
import 'widgets/app_loading_state.dart';

enum DebtFilter {
  all,
  owe,
  receive,
}

class DebtOverviewScreen extends StatefulWidget {
  const DebtOverviewScreen({super.key});

  @override
  State<DebtOverviewScreen> createState() =>
      _DebtOverviewScreenState();
}

class _DebtOverviewScreenState
    extends State<DebtOverviewScreen> {
  bool isLoading = true;
  bool isRefreshing = false;
  bool isSubmittingPayment = false;

  String? errorMessage;
  String currentUserEmail = '';
  String? submittingDebtId;

  DebtFilter selectedFilter = DebtFilter.all;

  List<_DebtItem> allDebts = [];

  @override
  void initState() {
    super.initState();
    loadDebts();
  }

  Future<void> loadDebts({
    bool showLoading = true,
  }) async {
    if (showLoading) {
      setState(() {
        isLoading = true;
        errorMessage = null;
      });
    }

    try {
      final profile = await ApiService.getProfile();
      final email = profile['email']?.toString() ?? '';

      final householdResponse =
          await ApiService.getHouseholds();

      final households = householdResponse
          .whereType<Map>()
          .map(
            (item) => Household.fromJson(
              Map<String, dynamic>.from(item),
            ),
          )
          .where((household) => household.isActive)
          .toList();

      final loadedDebts = <_DebtItem>[];

      for (final household in households) {
        var page = 1;

        while (true) {
          final response =
              await ApiService.getHouseholdDebts(
            household.id,
            page: page,
          );

          final results =
              List<dynamic>.from(response['results']);

          for (final item in results) {
            loadedDebts.add(
              _DebtItem(
                household: household,
                debt: Debt.fromJson(
                  Map<String, dynamic>.from(item),
                ),
              ),
            );
          }

          final next = response['next'];

          if (next == null ||
              next.toString().trim().isEmpty) {
            break;
          }

          page++;

          if (page > 20) {
            break;
          }
        }
      }

      if (!mounted) return;

      setState(() {
        currentUserEmail = email.toLowerCase().trim();
        allDebts = loadedDebts;
        isLoading = false;
        isRefreshing = false;
        errorMessage = null;
      });
    } catch (e) {
      if (!mounted) return;

      setState(() {
        isLoading = false;
        isRefreshing = false;
        errorMessage = getErrorMessage(e);
      });
    }
  }

  Future<void> refreshDebts() async {
    if (isRefreshing) return;

    setState(() {
      isRefreshing = true;
    });

    await loadDebts(showLoading: false);
  }

  Future<void> markDebtPaid(Debt debt) async {
    if (isSubmittingPayment) return;

    setState(() {
      isSubmittingPayment = true;
      submittingDebtId = debt.id;
    });

    try {
      await ApiService.markDebtPaid(debt.id);

      if (!mounted) return;

      showSnackBar(
        'Đã gửi yêu cầu xác nhận thanh toán.',
      );

      await loadDebts(showLoading: false);
    } catch (e) {
      if (!mounted) return;

      showSnackBar(getErrorMessage(e));
    } finally {
        if (mounted) {
          setState(() {
            isSubmittingPayment = false;
            submittingDebtId = null;
          });
        }
      }
  }

  Future<void> confirmPayment(Debt debt) async {
    if (isSubmittingPayment ||
        debt.pendingPaymentId == null) {
      return;
    }

    setState(() {
      isSubmittingPayment = true;
      submittingDebtId = debt.id;
    });

    try {
      await ApiService.confirmPayment(
        debt.pendingPaymentId!,
      );

      if (!mounted) return;

      showSnackBar('Đã xác nhận nhận tiền.');

      await loadDebts(showLoading: false);
    } catch (e) {
      if (!mounted) return;

      showSnackBar(getErrorMessage(e));
    } finally {
        if (mounted) {
          setState(() {
            isSubmittingPayment = false;
            submittingDebtId = null;
          });
        }
      }
  }

  Future<void> rejectPayment(Debt debt) async {
    if (isSubmittingPayment ||
        debt.pendingPaymentId == null) {
      return;
    }

    setState(() {
      isSubmittingPayment = true;
      submittingDebtId = debt.id;
    });

    try {
      await ApiService.rejectPayment(
        debt.pendingPaymentId!,
      );

      if (!mounted) return;

      showSnackBar('Đã từ chối yêu cầu thanh toán.');

      await loadDebts(showLoading: false);
    } catch (e) {
      if (!mounted) return;

      showSnackBar(getErrorMessage(e));
    } finally {
        if (mounted) {
          setState(() {
            isSubmittingPayment = false;
            submittingDebtId = null;
          });
        }
      }
  }

  void showSnackBar(String message) {
    ScaffoldMessenger.of(context).hideCurrentSnackBar();

    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message)),
    );
  }

  List<_DebtItem> get visibleDebts {
    if (selectedFilter == DebtFilter.owe) {
      return allDebts
          .where(
            (item) => item.isCurrentUserDebtor(
              currentUserEmail,
            ),
          )
          .toList();
    }

    if (selectedFilter == DebtFilter.receive) {
      return allDebts
          .where(
            (item) => item.isCurrentUserReceiver(
              currentUserEmail,
            ),
          )
          .toList();
    }

    return allDebts;
  }

  double get totalOwe {
    return allDebts
        .where(
          (item) => item.isCurrentUserDebtor(
            currentUserEmail,
          ),
        )
        .fold<double>(
          0,
          (sum, item) => sum + item.debt.amount,
        );
  }

  double get totalReceive {
    return allDebts
        .where(
          (item) => item.isCurrentUserReceiver(
            currentUserEmail,
          ),
        )
        .fold<double>(
          0,
          (sum, item) => sum + item.debt.amount,
        );
  }

  String getErrorMessage(Object error) {
    final message = error.toString();

    if (message.startsWith('Exception: ')) {
      return message.replaceFirst('Exception: ', '');
    }

    if (message.trim().isEmpty) {
      return 'Không thể tải danh sách công nợ';
    }

    return message;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        titleSpacing: 20,
        title: const Text('Công nợ'),
        actions: [
          IconButton(
            tooltip: 'Tải lại',
            onPressed: isLoading ? null : refreshDebts,
            icon: const Icon(Icons.refresh_rounded),
          ),
          const SizedBox(width: 8),
        ],
      ),
      body: buildBody(),
    );
  }

  Widget buildBody() {
    if (isLoading) {
      return const AppLoadingState(
        message: 'Đang tải công nợ...',
      );
    }

    if (errorMessage != null) {
      return AppErrorState(
        message: errorMessage!,
        onRetry: loadDebts,
      );
    }

    if (allDebts.isEmpty) {
      return RefreshIndicator(
        onRefresh: refreshDebts,
        color: AppColors.primary,
        child: ListView(
          physics: const AlwaysScrollableScrollPhysics(),
          children: const [
            SizedBox(height: 120),
            AppEmptyState(
              icon: Icons.verified_rounded,
              title: 'Không có công nợ',
              message:
                  'Hiện tại bạn chưa có khoản nợ nào cần trả hoặc cần nhận.',
            ),
          ],
        ),
      );
    }

    final debts = visibleDebts;

    return RefreshIndicator(
      onRefresh: refreshDebts,
      color: AppColors.primary,
      child: ListView(
        physics: const AlwaysScrollableScrollPhysics(),
        padding: const EdgeInsets.fromLTRB(
          20,
          12,
          20,
          120,
        ),
        children: [
          buildSummarySection(),
          const SizedBox(height: 18),
          buildFilterSection(),
          const SizedBox(height: 16),
          if (debts.isEmpty)
            Padding(
              padding: const EdgeInsets.only(top: 80),
              child: AppEmptyState(
                icon: selectedFilter == DebtFilter.owe
                    ? Icons.call_made_rounded
                    : Icons.call_received_rounded,
                title: selectedFilter == DebtFilter.owe
                    ? 'Không có khoản phải trả'
                    : 'Không có khoản được nhận',
                message:
                    'Bạn có thể đổi bộ lọc để xem các công nợ khác.',
              ),
            )
          else
            ...debts.map(
              (item) => Padding(
                padding: const EdgeInsets.only(
                  bottom: 12,
                ),
                child: buildDebtCard(item),
              ),
            ),
        ],
      ),
    );
  }

  Widget buildSummarySection() {
    return Container(
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [
            AppColors.primary,
            AppColors.primary.withValues(alpha: 0.82),
          ],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(28),
        boxShadow: [
          BoxShadow(
            color: AppColors.primary.withValues(alpha: 0.22),
            blurRadius: 22,
            offset: const Offset(0, 12),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Row(
            children: [
              Icon(
                Icons.sync_alt_rounded,
                color: Colors.white,
              ),
              SizedBox(width: 8),
              Text(
                'Tổng quan công nợ',
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 18,
                  fontWeight: FontWeight.w900,
                ),
              ),
            ],
          ),
          const SizedBox(height: 18),
          Row(
            children: [
              Expanded(
                child: buildSummaryCard(
                  label: 'Bạn cần trả',
                  value: formatMoney(totalOwe),
                  icon: Icons.call_made_rounded,
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: buildSummaryCard(
                  label: 'Bạn sẽ nhận',
                  value: formatMoney(totalReceive),
                  icon: Icons.call_received_rounded,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget buildSummaryCard({
    required String label,
    required String value,
    required IconData icon,
  }) {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: Colors.white.withValues(alpha: 0.14),
        borderRadius: BorderRadius.circular(22),
        border: Border.all(
          color: Colors.white.withValues(alpha: 0.18),
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(
            icon,
            color: Colors.white,
            size: 22,
          ),
          const SizedBox(height: 10),
          Text(
            label,
            style: TextStyle(
              color: Colors.white.withValues(alpha: 0.82),
              fontSize: 13,
              fontWeight: FontWeight.w700,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            value,
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
            style: const TextStyle(
              color: Colors.white,
              fontSize: 20,
              fontWeight: FontWeight.w900,
              letterSpacing: -0.4,
            ),
          ),
        ],
      ),
    );
  }

  Widget buildFilterSection() {
    return Container(
      padding: const EdgeInsets.all(6),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(
          color: AppColors.border,
        ),
      ),
      child: Row(
        children: [
          buildFilterItem(
            filter: DebtFilter.all,
            label: 'Tất cả',
          ),
          buildFilterItem(
            filter: DebtFilter.owe,
            label: 'Phải trả',
          ),
          buildFilterItem(
            filter: DebtFilter.receive,
            label: 'Được nhận',
          ),
        ],
      ),
    );
  }

  Widget buildFilterItem({
    required DebtFilter filter,
    required String label,
  }) {
    final isSelected = selectedFilter == filter;

    return Expanded(
      child: GestureDetector(
        onTap: () {
          setState(() {
            selectedFilter = filter;
          });
        },
        behavior: HitTestBehavior.opaque,
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 180),
          padding: const EdgeInsets.symmetric(
            vertical: 11,
          ),
          decoration: BoxDecoration(
            color: isSelected
                ? AppColors.primary
                : Colors.transparent,
            borderRadius: BorderRadius.circular(15),
          ),
          child: Text(
            label,
            textAlign: TextAlign.center,
            style: TextStyle(
              color: isSelected
                  ? Colors.white
                  : AppColors.textLight,
              fontSize: 13,
              fontWeight: FontWeight.w900,
            ),
          ),
        ),
      ),
    );
  }

  Widget buildDebtCard(_DebtItem item) {
    final debt = item.debt;

    final isOwe = item.isCurrentUserDebtor(
      currentUserEmail,
    );

    final title = isOwe
        ? 'Bạn nợ ${displayName(debt.toUserName, debt.toUserEmail)}'
        : '${displayName(debt.fromUserName, debt.fromUserEmail)} nợ bạn';

    final subtitle = buildDebtSubtitle(
      debt: debt,
      isOwe: isOwe,
    );

    return InkWell(
      onTap: () => showDebtDetail(item),
      borderRadius: BorderRadius.circular(24),
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(24),
          border: Border.all(
            color: debt.hasPendingPayment
                ? AppColors.primary.withValues(alpha: 0.40)
                : AppColors.border,
          ),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withValues(alpha: 0.035),
              blurRadius: 16,
              offset: const Offset(0, 8),
            ),
          ],
        ),
        child: Row(
          children: [
            buildAvatar(
              isOwe ? debt.toUserName : debt.fromUserName,
              isOwe
                  ? Icons.call_made_rounded
                  : Icons.call_received_rounded,
              isOwe,
            ),
            const SizedBox(width: 14),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: const TextStyle(
                      color: AppColors.textDark,
                      fontSize: 16,
                      fontWeight: FontWeight.w900,
                      letterSpacing: -0.2,
                    ),
                  ),
                  const SizedBox(height: 5),
                  Text(
                    subtitle,
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: TextStyle(
                      color: debt.hasPendingPayment
                          ? AppColors.primary
                          : AppColors.textLight,
                      fontSize: 13,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                  const SizedBox(height: 7),
                  Row(
                    children: [
                      const Icon(
                        Icons.groups_rounded,
                        size: 15,
                        color: AppColors.textLight,
                      ),
                      const SizedBox(width: 5),
                      Expanded(
                        child: Text(
                          item.household.name,
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                          style: const TextStyle(
                            color: AppColors.textLight,
                            fontSize: 12,
                            fontWeight: FontWeight.w700,
                          ),
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
            const SizedBox(width: 12),
            Column(
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                Text(
                  formatMoney(debt.amount),
                  style: TextStyle(
                    color: isOwe
                        ? Colors.redAccent
                        : AppColors.primary,
                    fontSize: 16,
                    fontWeight: FontWeight.w900,
                    letterSpacing: -0.2,
                  ),
                ),
                const SizedBox(height: 6),
                if (isSubmittingPayment &&
                    submittingDebtId == debt.id)
                  const SizedBox(
                    width: 18,
                    height: 18,
                    child: CircularProgressIndicator(
                      strokeWidth: 2,
                      color: AppColors.primary,
                    ),
                  )
                else
                  const Icon(
                    Icons.chevron_right_rounded,
                    color: AppColors.textLight,
                  ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  String buildDebtSubtitle({
    required Debt debt,
    required bool isOwe,
  }) {
    if (debt.hasPendingPayment) {
      return isOwe
          ? 'Đang chờ người nhận xác nhận'
          : 'Đang chờ bạn xác nhận thanh toán';
    }

    if (debt.expenseTitle.trim().isNotEmpty) {
      return 'Khoản chi: ${debt.expenseTitle}';
    }

    return isOwe
        ? 'Cần chuyển cho ${displayName(debt.toUserName, debt.toUserEmail)}'
        : 'Chờ ${displayName(debt.fromUserName, debt.fromUserEmail)} thanh toán';
  }

  Widget buildAvatar(
    String name,
    IconData fallbackIcon,
    bool isOwe,
  ) {
    final letter = name.trim().isNotEmpty
        ? name.trim()[0].toUpperCase()
        : '';

    return Container(
      width: 52,
      height: 52,
      decoration: BoxDecoration(
        color: isOwe
            ? Colors.redAccent.withValues(alpha: 0.10)
            : AppColors.primary.withValues(alpha: 0.10),
        borderRadius: BorderRadius.circular(20),
      ),
      child: Center(
        child: letter.isEmpty
            ? Icon(
                fallbackIcon,
                color: isOwe
                    ? Colors.redAccent
                    : AppColors.primary,
              )
            : Text(
                letter,
                style: TextStyle(
                  color: isOwe
                      ? Colors.redAccent
                      : AppColors.primary,
                  fontSize: 20,
                  fontWeight: FontWeight.w900,
                ),
              ),
      ),
    );
  }

  Future<void> showDebtDetail(_DebtItem item) async {
    final debt = item.debt;

    final isOwe = item.isCurrentUserDebtor(
      currentUserEmail,
    );

    final receiverName = displayName(
      debt.toUserName,
      debt.toUserEmail,
    );

    final debtorName = displayName(
      debt.fromUserName,
      debt.fromUserEmail,
    );

    await showModalBottomSheet<void>(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (sheetContext) {
        return SafeArea(
          child: Container(
            margin: const EdgeInsets.all(14),
            padding: const EdgeInsets.fromLTRB(
              18,
              16,
              18,
              18,
            ),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(28),
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withValues(alpha: 0.12),
                  blurRadius: 30,
                  offset: const Offset(0, 12),
                ),
              ],
            ),
            child: SingleChildScrollView(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Center(
                    child: Container(
                      width: 42,
                      height: 5,
                      decoration: BoxDecoration(
                        color: AppColors.border,
                        borderRadius:
                            BorderRadius.circular(999),
                      ),
                    ),
                  ),
                  const SizedBox(height: 18),
                  Text(
                    isOwe
                        ? 'Thông tin thanh toán'
                        : 'Chi tiết khoản được nhận',
                    style: const TextStyle(
                      color: AppColors.textDark,
                      fontSize: 20,
                      fontWeight: FontWeight.w900,
                      letterSpacing: -0.5,
                    ),
                  ),
                  const SizedBox(height: 14),
                  buildDetailRow(
                    icon: Icons.groups_rounded,
                    label: 'Nhóm',
                    value: item.household.name,
                  ),
                  buildDetailRow(
                    icon: Icons.receipt_long_rounded,
                    label: 'Khoản chi',
                    value: debt.expenseTitle,
                  ),
                  buildDetailRow(
                    icon: Icons.person_rounded,
                    label: 'Người nợ',
                    value: debtorName,
                  ),
                  buildDetailRow(
                    icon: Icons.account_balance_wallet_rounded,
                    label: 'Người nhận',
                    value: receiverName,
                  ),
                  buildDetailRow(
                    icon: Icons.payments_rounded,
                    label: 'Số tiền',
                    value: formatMoney(debt.amount),
                  ),
                  if (debt.hasPendingPayment)
                    buildPendingNotice(isOwe: isOwe),
                  const SizedBox(height: 10),
                  const Divider(height: 1),
                  const SizedBox(height: 14),
                  const Text(
                    'Thông tin ngân hàng người nhận',
                    style: TextStyle(
                      color: AppColors.textDark,
                      fontSize: 15,
                      fontWeight: FontWeight.w900,
                    ),
                  ),
                  const SizedBox(height: 10),
                  buildBankInfo(debt),
                  const SizedBox(height: 16),
                  buildPaymentActionSection(item),
                  const SizedBox(height: 18),
                  buildPaymentActions(
                    sheetContext: sheetContext,
                    debt: debt,
                    isOwe: isOwe,
                  ),
                ],
              ),
            ),
          ),
        );
      },
    );
  }

  Widget buildPaymentActionSection(_DebtItem item) {
    final debt = item.debt;

    final isOwe = item.isCurrentUserDebtor(
      currentUserEmail,
    );

    final isReceiver = item.isCurrentUserReceiver(
      currentUserEmail,
    );

    final isSubmitting =
        isSubmittingPayment && submittingDebtId == debt.id;

    if (debt.hasPendingPayment) {
      if (isReceiver) {
        return Row(
          children: [
            Expanded(
              child: OutlinedButton.icon(
                onPressed: isSubmitting
                    ? null
                    : () => rejectPayment(debt),
                icon: const Icon(Icons.close_rounded),
                label: const Text('Từ chối'),
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: FilledButton.icon(
                onPressed: isSubmitting
                    ? null
                    : () => confirmPayment(debt),
                icon: isSubmitting
                    ? const SizedBox(
                        width: 18,
                        height: 18,
                        child: CircularProgressIndicator(
                          strokeWidth: 2,
                          color: Colors.white,
                        ),
                      )
                    : const Icon(Icons.check_rounded),
                label: const Text('Xác nhận'),
              ),
            ),
          ],
        );
      }

      return Container(
        width: double.infinity,
        padding: const EdgeInsets.all(14),
        decoration: BoxDecoration(
          color: AppColors.primary.withValues(alpha: 0.08),
          borderRadius: BorderRadius.circular(18),
          border: Border.all(
            color: AppColors.primary.withValues(alpha: 0.18),
          ),
        ),
        child: const Row(
          children: [
            Icon(
              Icons.hourglass_top_rounded,
              color: AppColors.primary,
            ),
            SizedBox(width: 10),
            Expanded(
              child: Text(
                'Đang chờ người nhận xác nhận thanh toán.',
                style: TextStyle(
                  color: AppColors.primary,
                  fontWeight: FontWeight.w800,
                  height: 1.35,
                ),
              ),
            ),
          ],
        ),
      );
    }

    if (isOwe) {
      return SizedBox(
        width: double.infinity,
        height: 52,
        child: FilledButton.icon(
          onPressed: isSubmitting
              ? null
              : () => markDebtPaid(debt),
          icon: isSubmitting
              ? const SizedBox(
                  width: 18,
                  height: 18,
                  child: CircularProgressIndicator(
                    strokeWidth: 2,
                    color: Colors.white,
                  ),
                )
              : const Icon(Icons.payments_rounded),
          label: Text(
            isSubmitting
                ? 'Đang gửi...'
                : 'Tôi đã thanh toán',
          ),
        ),
      );
    }

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: AppColors.background,
        borderRadius: BorderRadius.circular(18),
        border: Border.all(
          color: AppColors.border,
        ),
      ),
      child: const Text(
        'Chờ người nợ gửi yêu cầu xác nhận thanh toán.',
        style: TextStyle(
          color: AppColors.textLight,
          fontWeight: FontWeight.w700,
          height: 1.35,
        ),
      ),
    );
  }

  Widget buildPendingNotice({
    required bool isOwe,
  }) {
    return Container(
      width: double.infinity,
      margin: const EdgeInsets.only(top: 6),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: AppColors.primary.withValues(alpha: 0.08),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: AppColors.primary.withValues(alpha: 0.18),
        ),
      ),
      child: Text(
        isOwe
            ? 'Bạn đã báo thanh toán. Công nợ sẽ được đóng sau khi người nhận xác nhận.'
            : 'Người nợ đã báo thanh toán. Hãy xác nhận nếu bạn đã nhận tiền.',
        style: const TextStyle(
          color: AppColors.primary,
          fontSize: 13,
          fontWeight: FontWeight.w800,
          height: 1.4,
        ),
      ),
    );
  }

  Widget buildPaymentActions({
    required BuildContext sheetContext,
    required Debt debt,
    required bool isOwe,
  }) {
    if (isOwe && debt.canMarkPaid) {
      return SizedBox(
        width: double.infinity,
        child: ElevatedButton.icon(
          onPressed: isSubmittingPayment
              ? null
              : () {
                  Navigator.pop(sheetContext);
                  markDebtPaid(debt);
                },
          icon: const Icon(Icons.check_circle_rounded),
          label: const Text('Tôi đã thanh toán'),
          style: ElevatedButton.styleFrom(
            backgroundColor: AppColors.primary,
            foregroundColor: Colors.white,
            padding: const EdgeInsets.symmetric(vertical: 14),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(16),
            ),
          ),
        ),
      );
    }

    if (!isOwe && debt.canConfirmPayment) {
      return Row(
        children: [
          Expanded(
            child: OutlinedButton.icon(
              onPressed: isSubmittingPayment
                  ? null
                  : () {
                      Navigator.pop(sheetContext);
                      rejectPayment(debt);
                    },
              icon: const Icon(Icons.close_rounded),
              label: const Text('Từ chối'),
              style: OutlinedButton.styleFrom(
                foregroundColor: Colors.redAccent,
                side: const BorderSide(color: Colors.redAccent),
                padding: const EdgeInsets.symmetric(vertical: 14),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(16),
                ),
              ),
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: ElevatedButton.icon(
              onPressed: isSubmittingPayment
                  ? null
                  : () {
                      Navigator.pop(sheetContext);
                      confirmPayment(debt);
                    },
              icon: const Icon(Icons.done_rounded),
              label: const Text('Xác nhận'),
              style: ElevatedButton.styleFrom(
                backgroundColor: AppColors.primary,
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(vertical: 14),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(16),
                ),
              ),
            ),
          ),
        ],
      );
    }

    if (debt.hasPendingPayment) {
      return const SizedBox.shrink();
    }

    return const SizedBox.shrink();
  }

  Widget buildDetailRow({
    required IconData icon,
    required String label,
    required String value,
  }) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 11),
      child: Row(
        children: [
          Icon(
            icon,
            color: AppColors.primary,
            size: 20,
          ),
          const SizedBox(width: 10),
          SizedBox(
            width: 92,
            child: Text(
              label,
              style: const TextStyle(
                color: AppColors.textLight,
                fontSize: 13,
                fontWeight: FontWeight.w700,
              ),
            ),
          ),
          Expanded(
            child: Text(
              value.trim().isEmpty ? 'Chưa có' : value,
              textAlign: TextAlign.right,
              style: const TextStyle(
                color: AppColors.textDark,
                fontSize: 14,
                fontWeight: FontWeight.w900,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget buildBankInfo(Debt debt) {
    final hasBankInfo =
        debt.bankName.trim().isNotEmpty ||
            debt.bankAccountNumber.trim().isNotEmpty ||
            debt.bankAccountHolder.trim().isNotEmpty;

    if (!hasBankInfo) {
      return Container(
        width: double.infinity,
        padding: const EdgeInsets.all(14),
        decoration: BoxDecoration(
          color: AppColors.background,
          borderRadius: BorderRadius.circular(18),
          border: Border.all(
            color: AppColors.border,
          ),
        ),
        child: const Text(
          'Người nhận chưa cập nhật thông tin ngân hàng.',
          style: TextStyle(
            color: AppColors.textLight,
            fontWeight: FontWeight.w700,
            height: 1.4,
          ),
        ),
      );
    }

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: AppColors.background,
        borderRadius: BorderRadius.circular(18),
        border: Border.all(
          color: AppColors.border,
        ),
      ),
      child: Column(
        children: [
          buildBankRow(
            label: 'Ngân hàng',
            value: debt.bankName,
          ),
          buildBankRow(
            label: 'Chủ tài khoản',
            value: debt.bankAccountHolder,
          ),
          buildBankRow(
            label: 'Số tài khoản',
            value: debt.bankAccountNumber,
            canCopy: debt.bankAccountNumber
                .trim()
                .isNotEmpty,
          ),
        ],
      ),
    );
  }

  Widget buildBankRow({
    required String label,
    required String value,
    bool canCopy = false,
  }) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 9),
      child: Row(
        children: [
          SizedBox(
            width: 105,
            child: Text(
              label,
              style: const TextStyle(
                color: AppColors.textLight,
                fontSize: 13,
                fontWeight: FontWeight.w700,
              ),
            ),
          ),
          Expanded(
            child: Text(
              value.trim().isEmpty ? 'Chưa có' : value,
              textAlign: TextAlign.right,
              style: const TextStyle(
                color: AppColors.textDark,
                fontSize: 14,
                fontWeight: FontWeight.w900,
              ),
            ),
          ),
          if (canCopy) ...[
            const SizedBox(width: 8),
            InkWell(
              borderRadius: BorderRadius.circular(10),
              onTap: () async {
                await Clipboard.setData(
                  ClipboardData(text: value),
                );

                if (!mounted) return;

                ScaffoldMessenger.of(context)
                    .hideCurrentSnackBar();

                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(
                    content:
                        Text('Đã sao chép số tài khoản'),
                  ),
                );
              },
              child: const Padding(
                padding: EdgeInsets.all(6),
                child: Icon(
                  Icons.copy_rounded,
                  color: AppColors.primary,
                  size: 18,
                ),
              ),
            ),
          ],
        ],
      ),
    );
  }

  String displayName(
    String name,
    String email,
  ) {
    if (name.trim().isNotEmpty) {
      return name.trim();
    }

    if (email.trim().isNotEmpty) {
      return email.trim();
    }

    return 'Người dùng';
  }

  String formatMoney(double value) {
    final number = value.round().toString();

    final formatted = number.replaceAllMapped(
      RegExp(r'(\d{1,3})(?=(\d{3})+(?!\d))'),
      (match) => '${match[1]}.',
    );

    return '$formattedđ';
  }
}

class _DebtItem {
  final Household household;
  final Debt debt;

  _DebtItem({
    required this.household,
    required this.debt,
  });

  bool isCurrentUserDebtor(String email) {
    return debt.fromUserEmail.toLowerCase().trim() ==
        email.toLowerCase().trim();
  }

  bool isCurrentUserReceiver(String email) {
    return debt.toUserEmail.toLowerCase().trim() ==
        email.toLowerCase().trim();
  }
}
