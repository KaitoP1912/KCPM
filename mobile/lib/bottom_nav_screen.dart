import 'package:flutter/material.dart';

import 'activity_screen.dart';
import 'app_theme.dart';
import 'home_screen.dart';
import 'services/api_service.dart';
import 'profile_screen.dart';

class BottomNavScreen extends StatefulWidget {
  const BottomNavScreen({super.key});

  @override
  State<BottomNavScreen> createState() => _BottomNavScreenState();
}

class _BottomNavScreenState extends State<BottomNavScreen> {
  int currentIndex = 0;

  int unreadNotificationCount = 0;
  late final List<Widget> screens;

  @override
  void initState() {
    super.initState();

    screens = const [
      HomeScreen(),
      ActivityScreen(),
      AddExpenseEntryScreen(),
      DebtOverviewScreen(),
      ProfileScreen(),
    ];

    loadUnreadCount();
  }

  Future<void> loadUnreadCount() async {
    try {
      final count = await ApiService.getUnreadNotificationCount();

      if (!mounted) return;

      setState(() {
        unreadNotificationCount = count;
      });
    } catch (_) {}
  }

  Future<void> changeTab(int index) async {
    setState(() {
      currentIndex = index;
    });

    if (index == 1) {
      await loadUnreadCount();
    }
  }

  @override
  Widget build(BuildContext context) {

    return Scaffold(
      extendBody: true,
      body: IndexedStack(
        index: currentIndex,
        children: screens,
      ),
      bottomNavigationBar: SafeArea(
        top: false,
        child: Container(
          height: 86,
          margin: const EdgeInsets.fromLTRB(18, 0, 18, 14),
          padding: const EdgeInsets.symmetric(
            horizontal: 10,
            vertical: 8,
          ),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(28),
            boxShadow: [
              BoxShadow(
                color: Colors.black.withValues(alpha: 0.08),
                blurRadius: 28,
                offset: const Offset(0, 12),
              ),
            ],
          ),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              buildNavItem(
                index: 0,
                icon: Icons.home_rounded,
                label: 'Trang chủ',
              ),
              buildNavItem(
                index: 1,
                icon: Icons.receipt_long_rounded,
                label: 'Hoạt động',
                badgeCount: unreadNotificationCount,
              ),
              buildCenterButton(),
              buildNavItem(
                index: 3,
                icon: Icons.sync_alt_rounded,
                label: 'Công nợ',
              ),
              buildNavItem(
                index: 4,
                icon: Icons.person_rounded,
                label: 'Cá nhân',
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget buildCenterButton() {
    final isActive = currentIndex == 2;

    return Expanded(
      child: GestureDetector(
        onTap: () => changeTab(2),
        behavior: HitTestBehavior.opaque,
        child: Transform.translate(
          offset: const Offset(0, -18),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              AnimatedContainer(
                duration: const Duration(milliseconds: 220),
                width: 58,
                height: 58,
                decoration: BoxDecoration(
                  color: AppColors.primary,
                  shape: BoxShape.circle,
                  boxShadow: [
                    BoxShadow(
                      color: AppColors.primary.withValues(alpha: 0.32),
                      blurRadius: 22,
                      offset: const Offset(0, 10),
                    ),
                  ],
                ),
                child: const Icon(
                  Icons.add_rounded,
                  color: Colors.white,
                  size: 34,
                ),
              ),
              const SizedBox(height: 6),
              AnimatedContainer(
                duration: const Duration(milliseconds: 220),
                width: isActive ? 6 : 0,
                height: isActive ? 6 : 0,
                decoration: const BoxDecoration(
                  color: AppColors.primary,
                  shape: BoxShape.circle,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget buildNavItem({
    required int index,
    required IconData icon,
    required String label,
    int badgeCount = 0,
  }) {
    final isActive = currentIndex == index;

    return Expanded(
      child: GestureDetector(
        onTap: () => changeTab(index),
        behavior: HitTestBehavior.opaque,
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Stack(
              clipBehavior: Clip.none,
              children: [
                AnimatedContainer(
                  duration: const Duration(milliseconds: 220),
                  padding: const EdgeInsets.all(9),
                  decoration: BoxDecoration(
                    color: isActive
                        ? AppColors.primary.withValues(alpha: 0.10)
                        : Colors.transparent,
                    borderRadius: BorderRadius.circular(16),
                  ),
                  child: Icon(
                    icon,
                    size: 23,
                    color: isActive
                        ? AppColors.primary
                        : AppColors.textLight,
                  ),
                ),

                if (badgeCount > 0)
                  Positioned(
                    top: -4,
                    right: -6,
                    child: Container(
                      constraints: const BoxConstraints(
                        minWidth: 19,
                        minHeight: 19,
                      ),
                      padding: const EdgeInsets.symmetric(
                        horizontal: 5,
                      ),
                      decoration: BoxDecoration(
                        color: Colors.red,
                        borderRadius: BorderRadius.circular(999),
                        border: Border.all(
                          color: Colors.white,
                          width: 2,
                        ),
                      ),
                      child: Center(
                        child: Text(
                          badgeCount > 99
                              ? '99+'
                              : badgeCount.toString(),
                          style: const TextStyle(
                            color: Colors.white,
                            fontSize: 10,
                            fontWeight: FontWeight.w900,
                          ),
                        ),
                      ),
                    ),
                  ),
              ],
            ),
            const SizedBox(height: 5),
            AnimatedDefaultTextStyle(
              duration: const Duration(milliseconds: 220),
              style: TextStyle(
                fontSize: 11,
                fontWeight: isActive
                    ? FontWeight.w800
                    : FontWeight.w600,
                color: isActive
                    ? AppColors.primary
                    : AppColors.textLight,
                letterSpacing: -0.1,
              ),
              child: Text(
                label,
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
              ),
            ),
            const SizedBox(height: 4),
            AnimatedContainer(
              duration: const Duration(milliseconds: 220),
              width: isActive ? 5 : 0,
              height: isActive ? 5 : 0,
              decoration: const BoxDecoration(
                color: AppColors.primary,
                shape: BoxShape.circle,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class AddExpenseEntryScreen extends StatelessWidget {
  const AddExpenseEntryScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return const _SimpleFeatureScreen(
      title: 'Thêm chi tiêu',
      icon: Icons.add_rounded,
      description:
          'Chọn một nhóm ở Trang chủ để thêm khoản chi vào nhóm đó.',
    );
  }
}

class DebtOverviewScreen extends StatelessWidget {
  const DebtOverviewScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return const _SimpleFeatureScreen(
      title: 'Công nợ',
      icon: Icons.sync_alt_rounded,
      description:
          'Tổng quan ai nợ ai sẽ được gom tại màn hình này.',
    );
  }
}

class _SimpleFeatureScreen extends StatelessWidget {
  final String title;
  final IconData icon;
  final String description;

  const _SimpleFeatureScreen({
    required this.title,
    required this.icon,
    required this.description,
  });

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        titleSpacing: 20,
        title: Text(title),
      ),
      body: Center(
        child: Container(
          margin: const EdgeInsets.all(24),
          padding: const EdgeInsets.all(30),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(30),
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Container(
                width: 72,
                height: 72,
                decoration: BoxDecoration(
                  color: AppColors.primary.withValues(alpha: 0.10),
                  borderRadius: BorderRadius.circular(24),
                ),
                child: Icon(
                  icon,
                  color: AppColors.primary,
                  size: 34,
                ),
              ),
              const SizedBox(height: 20),
              Text(
                title,
                style: const TextStyle(
                  fontSize: 22,
                  fontWeight: FontWeight.w900,
                  color: AppColors.textDark,
                  letterSpacing: -0.5,
                ),
              ),
              const SizedBox(height: 10),
              Text(
                description,
                textAlign: TextAlign.center,
                style: const TextStyle(
                  color: AppColors.textLight,
                  fontSize: 15,
                  fontWeight: FontWeight.w600,
                  height: 1.45,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}