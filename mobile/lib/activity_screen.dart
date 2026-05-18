import 'package:flutter/material.dart';

import 'app_theme.dart';
import 'services/api_service.dart';
import 'widgets/app_empty_state.dart';
import 'widgets/app_error_state.dart';
import 'widgets/app_loading_state.dart';

class ActivityScreen extends StatefulWidget {
  final String? householdId;

  const ActivityScreen({
    super.key,
    this.householdId,
  });

  @override
  State<ActivityScreen> createState() => _ActivityScreenState();
}

class _ActivityScreenState extends State<ActivityScreen>
    with SingleTickerProviderStateMixin {
  late TabController tabController;

  bool isLoadingActivities = true;
  bool isLoadingNotifications = true;
  
  String? activityError;
  String? notificationError;

  List<dynamic> activities = [];
  List<dynamic> notifications = [];

  bool get isGroupOnly => widget.householdId != null;

  @override
  void initState() {
    super.initState();

    tabController = TabController(
      length: isGroupOnly ? 1 : 2,
      vsync: this,
    );

    loadActivities();

    if (!isGroupOnly) {
      loadNotifications();
    }
  }

  @override
  void dispose() {
    tabController.dispose();
    super.dispose();
  }

  Future<void> loadActivities() async {
    if (!mounted) return;

    setState(() {
      isLoadingActivities = true;
      activityError = null;
    });

    try {
      final data = isGroupOnly
          ? await ApiService.getActivities(
              widget.householdId!,
            )
          : await ApiService.getAllActivities();

      if (!mounted) return;

      setState(() {
        activities = data;
        isLoadingActivities = false;
        activityError = null;
      });
    } catch (e) {
      debugPrint(e.toString());

      if (!mounted) return;

      setState(() {
        activityError = 'Không thể tải hoạt động';
        isLoadingActivities = false;
      });
    }
  }

  Future<void> loadNotifications() async {
    if (!mounted) return;

    setState(() {
      isLoadingNotifications = true;
      notificationError = null;
    });

    try {
      final data = await ApiService.getNotifications();

      if (!mounted) return;

      setState(() {
        notifications = data;
        isLoadingNotifications = false;
        notificationError = null;
      });
    } catch (e) {
      debugPrint(e.toString());

      if (!mounted) return;

      setState(() {
        notificationError = 'Không thể tải thông báo';
        isLoadingNotifications = false;
      });
    }
  }

  Future<void> refreshCurrent() async {
    if (isGroupOnly) {
      await loadActivities();
      return;
    }

    if (tabController.index == 0) {
      await loadActivities();
    } else {
      await loadNotifications();
    }
  }

  IconData getIcon(String type) {
    switch (type) {
      case 'group_created':
        return Icons.group_add_rounded;
      case 'expense_created':
        return Icons.receipt_long_rounded;
      case 'expense_updated':
        return Icons.edit_note_rounded;
      case 'expense_deleted':
        return Icons.delete_outline_rounded;
      case 'member_joined':
      case 'added_to_group':
      case 'member_added_to_group':
        return Icons.person_add_alt_1_rounded;
      case 'debt_created':
        return Icons.account_balance_wallet_rounded;
      case 'payment_received':
      case 'payment_sent':
      case 'payment_created':
      case 'payment_confirmed':
        return Icons.payments_rounded;
      case 'debt_reminder_received':
      case 'debt_reminder_sent':
        return Icons.notifications_active_rounded;
      default:
        return Icons.history_rounded;
    }
  }

  Color getIconColor(String type) {
    switch (type) {
      case 'group_created':
        return Colors.indigo;
      case 'expense_created':
        return AppColors.primary;
      case 'expense_updated':
        return Colors.amber.shade800;
      case 'expense_deleted':
        return Colors.red;
      case 'member_joined':
      case 'added_to_group':
      case 'member_added_to_group':
        return Colors.blue;
      case 'debt_created':
        return Colors.deepOrange;
      case 'payment_received':
      case 'payment_sent':
      case 'payment_created':
      case 'payment_confirmed':
        return Colors.green;
      case 'debt_reminder_received':
      case 'debt_reminder_sent':
        return Colors.orange;
      default:
        return AppColors.textLight;
    }
  }

  String formatMoney(dynamic amount) {
    if (amount == null) return '';

    final value = amount.toString().split('.').first;

    return '${value.replaceAllMapped(
      RegExp(r'\B(?=(\d{3})+(?!\d))'),
      (match) => '.',
    )}đ';
  }

  String formatTime(dynamic value) {
    if (value == null) return '';

    try {
      final date = DateTime.parse(value.toString()).toLocal();
      final now = DateTime.now();
      final diff = now.difference(date);

      if (diff.inMinutes < 1) return 'Vừa xong';
      if (diff.inMinutes < 60) return '${diff.inMinutes} phút trước';
      if (diff.inHours < 24) return '${diff.inHours} giờ trước';
      if (diff.inDays < 7) return '${diff.inDays} ngày trước';

      return '${date.day}/${date.month}/${date.year}';
    } catch (_) {
      return value.toString();
    }
  }

  Widget buildActivityCard(dynamic item) {
    final activity = Map<String, dynamic>.from(item);
    final type = activity['activity_type']?.toString() ?? '';
    final amount = activity['amount'];
    final householdName = activity['household_name'];
    final iconColor = getIconColor(type);

    return buildFeedCard(
      icon: getIcon(type),
      iconColor: iconColor,
      title: activity['title']?.toString() ?? 'Hoạt động mới',
      amount: amount,
      time: activity['created_at'],
      householdName: householdName,
      isUnread: false,
      level: null,
    );
  }

  Widget buildNotificationCard(dynamic item) {
    final notification = Map<String, dynamic>.from(item);
    final type = notification['notification_type']?.toString() ?? '';
    final amount = notification['amount'];
    final householdName = notification['household_name'];
    final isRead = notification['is_read'] == true;
    final level = notification['level']?.toString();
    final iconColor = getIconColor(type);

    return GestureDetector(
      onTap: () async {
        final id = notification['id']?.toString();

        if (id != null && !isRead) {
          await ApiService.markNotificationAsRead(id);
          await loadNotifications();
        }
      },
      child: buildFeedCard(
        icon: getIcon(type),
        iconColor: iconColor,
        title: notification['title']?.toString() ?? 'Thông báo mới',
        amount: amount,
        time: notification['created_at'],
        householdName: householdName,
        isUnread: !isRead,
        level: level,
      ),
    );
  }

  Widget buildFeedCard({
    required IconData icon,
    required Color iconColor,
    required String title,
    required dynamic amount,
    required dynamic time,
    required dynamic householdName,
    required bool isUnread,
    required String? level,
  }) {
    final isPushLevel = level == 'push';

    return Container(
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: isUnread ? AppColors.primary.withValues(alpha: 0.05) : Colors.white,
        borderRadius: BorderRadius.circular(24),
        border: Border.all(
          color: isUnread
              ? AppColors.primary.withValues(alpha: 0.22)
              : Colors.transparent,
        ),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.03),
            blurRadius: 20,
            offset: const Offset(0, 8),
          ),
        ],
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Stack(
            clipBehavior: Clip.none,
            children: [
              Container(
                width: 52,
                height: 52,
                decoration: BoxDecoration(
                  color: iconColor.withValues(alpha: 0.12),
                  borderRadius: BorderRadius.circular(18),
                ),
                child: Icon(
                  icon,
                  color: iconColor,
                ),
              ),
              if (isUnread)
                Positioned(
                  top: -2,
                  right: -2,
                  child: Container(
                    width: 11,
                    height: 11,
                    decoration: const BoxDecoration(
                      color: Colors.red,
                      shape: BoxShape.circle,
                    ),
                  ),
                ),
            ],
          ),
          const SizedBox(width: 14),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                if (isPushLevel) ...[
                  Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 8,
                      vertical: 3,
                    ),
                    decoration: BoxDecoration(
                      color: Colors.orange.withValues(alpha: 0.12),
                      borderRadius: BorderRadius.circular(999),
                    ),
                    child: const Text(
                      'Quan trọng',
                      style: TextStyle(
                        color: Colors.orange,
                        fontSize: 11,
                        fontWeight: FontWeight.w900,
                      ),
                    ),
                  ),
                  const SizedBox(height: 8),
                ],
                Text(
                  title,
                  style: const TextStyle(
                    fontSize: 15,
                    fontWeight: FontWeight.w800,
                    color: AppColors.textDark,
                  ),
                ),
                if (householdName != null) ...[
                  const SizedBox(height: 6),
                  Text(
                    householdName.toString(),
                    style: const TextStyle(
                      color: AppColors.textLight,
                      fontSize: 12,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                ],
                const SizedBox(height: 8),
                Row(
                  children: [
                    if (amount != null) ...[
                      Text(
                        formatMoney(amount),
                        style: const TextStyle(
                          color: AppColors.primary,
                          fontWeight: FontWeight.w900,
                        ),
                      ),
                      const SizedBox(width: 8),
                      const Text(
                        '•',
                        style: TextStyle(
                          color: AppColors.textLight,
                        ),
                      ),
                      const SizedBox(width: 8),
                    ],
                    Expanded(
                      child: Text(
                        formatTime(time),
                        style: const TextStyle(
                          color: AppColors.textLight,
                          fontWeight: FontWeight.w600,
                          fontSize: 12,
                        ),
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget buildList({
    required bool isLoading,
    required List<dynamic> items,
    required Widget Function(dynamic item) builder,
    required String emptyTitle,
    required String emptyDescription,
    required String? errorMessage,
    required Future<void> Function() onRetry,
    required IconData emptyIcon,
  }) {
    if (isLoading) {
      return const AppLoadingState(
        message: 'Đang tải dữ liệu...',
      );
    }

    if (errorMessage != null) {
      return AppErrorState(
        message: errorMessage,
        onRetry: onRetry,
      );
    }

    if (items.isEmpty) {
      return RefreshIndicator(
        onRefresh: refreshCurrent,
        child: ListView(
          physics:
              const AlwaysScrollableScrollPhysics(),
          children: [
            SizedBox(
              height:
                  MediaQuery.of(context).size.height *
                  0.62,
              child: AppEmptyState(
                icon: emptyIcon,
                title: emptyTitle,
                message: emptyDescription,
              ),
            ),
          ],
        ),
      );
    }

    return RefreshIndicator(
      onRefresh: refreshCurrent,
      child: ListView.separated(
        physics:
            const AlwaysScrollableScrollPhysics(),
        padding:
            const EdgeInsets.fromLTRB(20, 18, 20, 110),
        itemCount: items.length,
        separatorBuilder: (context, index) =>
            const SizedBox(height: 14),
        itemBuilder: (context, index) {
          return builder(items[index]);
        },
      ),
    );
  }

  Widget buildHeader() {
    return Container(
      padding: const EdgeInsets.fromLTRB(20, 18, 20, 12),
      child: Row(
        children: [
          const Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Hoạt động',
                  style: TextStyle(
                    fontSize: 28,
                    fontWeight: FontWeight.w900,
                    color: AppColors.textDark,
                    letterSpacing: -0.8,
                  ),
                ),
                SizedBox(height: 6),
                Text(
                  'Hoạt động chung và thông báo riêng của bạn.',
                  style: TextStyle(
                    color: AppColors.textLight,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ],
            ),
          ),
          IconButton(
            onPressed: isLoadingNotifications
                ? null
                : () async {
                    await ApiService.markAllNotificationsAsRead();
                    await loadNotifications();
                  },
            icon: const Icon(Icons.done_all_rounded),
            tooltip: 'Đánh dấu đã đọc',
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final tabs = isGroupOnly
        ? const [
            Tab(text: 'Hoạt động nhóm'),
          ]
        : const [
            Tab(text: 'Hoạt động chung'),
            Tab(text: 'Thông báo riêng'),
          ];

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: isGroupOnly
          ? AppBar(
              title: const Text('Hoạt động'),
            )
          : null,
      body: SafeArea(
        child: Column(
          children: [
            if (!isGroupOnly) buildHeader(),
            Container(
              margin: const EdgeInsets.symmetric(horizontal: 20),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(18),
              ),
              child: TabBar(
                controller: tabController,
                tabs: tabs,
                labelColor: AppColors.primary,
                unselectedLabelColor: AppColors.textLight,
                indicatorColor: AppColors.primary,
                indicatorWeight: 3,
                dividerColor: Colors.transparent,
                labelStyle: const TextStyle(
                  fontWeight: FontWeight.w900,
                  fontSize: 13,
                ),
                unselectedLabelStyle: const TextStyle(
                  fontWeight: FontWeight.w700,
                  fontSize: 13,
                ),
              ),
            ),
            Expanded(
              child: TabBarView(
                controller: tabController,
                children: isGroupOnly
                    ? [
                        buildList(
                          isLoading: isLoadingActivities,
                          items: activities,
                          errorMessage: activityError,
                          onRetry: loadActivities,
                          emptyIcon: Icons.history_rounded,
                          builder: buildActivityCard,
                          emptyTitle: 'Chưa có hoạt động',
                          emptyDescription:
                              'Khi nhóm có khoản chi hoặc thành viên mới, hoạt động sẽ hiện ở đây.',
                        ),
                      ]
                    : [
                        buildList(
                          isLoading: isLoadingActivities,
                          items: activities,
                          errorMessage: activityError,
                          onRetry: loadActivities,
                          emptyIcon: Icons.history_rounded,
                          builder: buildActivityCard,
                          emptyTitle: 'Chưa có hoạt động chung',
                          emptyDescription:
                              'Các hoạt động công khai trong nhóm sẽ hiện ở đây.',
                        ),
                        buildList(
                          isLoading: isLoadingNotifications,
                          items: notifications,
                          errorMessage: notificationError,
                          onRetry: loadNotifications,
                          emptyIcon:
                              Icons.notifications_none_rounded,
                          builder: buildNotificationCard,
                          emptyTitle: 'Chưa có thông báo riêng',
                          emptyDescription:
                              'Nhắc nợ, thanh toán và thông báo cá nhân sẽ hiện ở đây.',
                        ),
                      ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}