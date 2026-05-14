import 'package:flutter/material.dart';

import 'app_theme.dart';
import 'create_household_screen.dart';
import 'household_detail_screen.dart';
import 'models/household.dart';
import 'services/api_service.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() =>
      _HomeScreenState();
}

class _HomeScreenState
    extends State<HomeScreen> {
  List<Household> households = [];

  bool isLoading = true;

  @override
  void initState() {
    super.initState();

    loadHouseholds();
  }

  Future<void> loadHouseholds() async {
    setState(() {
      isLoading = true;
    });

    try {
      final data =
          await ApiService.getHouseholds();

      final loadedHouseholds = data
          .map<Household>(
            (json) => Household.fromJson(json),
          )
          .toList();

      if (!mounted) return;

      setState(() {
        households = loadedHouseholds;
        isLoading = false;
      });
    } catch (e) {
      debugPrint(e.toString());

      if (!mounted) return;

      setState(() {
        isLoading = false;
      });

      ScaffoldMessenger.of(context)
          .showSnackBar(
        const SnackBar(
          content: Text(
            'Không thể tải danh sách nhóm',
          ),
        ),
      );
    }
  }

  Future<void> openCreateHouseholdScreen() async {
    final result = await Navigator.push(
      context,
      MaterialPageRoute(
        builder: (_) =>
            const CreateHouseholdScreen(),
      ),
    );

    if (result == true) {
      await loadHouseholds();
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor:
          AppColors.background,
      appBar: AppBar(
        titleSpacing: 20,
        title: Row(
          children: [
            Container(
              width: 34,
              height: 34,
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(10),
              ),
              child: ClipRRect(
                borderRadius: BorderRadius.circular(10),
                child: Image.asset(
                  'assets/images/logo.png',
                  fit: BoxFit.cover,
                ),
              ),
            ),
            const SizedBox(width: 12),
            const Text(
              'Chung Ví',
              style: TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.w900,
                letterSpacing: -0.5,
              ),
            ),
          ],
        ),
        actions: [
          Padding(
            padding: const EdgeInsets.only(right: 12),
            child: IconButton(
              onPressed: loadHouseholds,
              style: IconButton.styleFrom(
                backgroundColor: Colors.white,
              ),
              icon: const Icon(
                Icons.refresh_rounded,
                color: AppColors.textDark,
              ),
            ),
          ),
        ],
      ),
      floatingActionButton:
          FloatingActionButton(
        elevation: 0,
        backgroundColor:
            AppColors.primary,
        onPressed:
            openCreateHouseholdScreen,
        child: const Icon(
          Icons.add_rounded,
          color: Colors.white,
        ),
      ),
      body: RefreshIndicator(
        onRefresh: loadHouseholds,
        child: isLoading
            ? const Center(
                child:
                    CircularProgressIndicator(),
              )
            : households.isEmpty
                ? buildEmptyState()
                : ListView(
                    padding:
                        const EdgeInsets.all(
                      20,
                    ),
                    children: [
                      buildHeader(),
                      const SizedBox(
                          height: 26),
                      ...households.map(
                        (household) =>
                            buildHouseholdCard(
                          household,
                        ),
                      ),
                      const SizedBox(
                          height: 120),
                    ],
                  ),
      ),
    );
  }

  Widget buildHeader() {
    return Container(
      padding:
          const EdgeInsets.all(24),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [
            AppColors.primary,
            AppColors.secondary,
          ],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius:
            BorderRadius.circular(30),
      ),
      child: Column(
        crossAxisAlignment:
            CrossAxisAlignment.start,
        children: [
          const Text(
            'Xin chào 👋',
            style: TextStyle(
              color: Colors.white70,
              fontSize: 15,
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: 10),
          const Text(
            'Quản lý chi tiêu nhóm\nmột cách rõ ràng',
            style: TextStyle(
              color: Colors.white,
              fontSize: 28,
              fontWeight: FontWeight.w900,
              height: 1.2,
              letterSpacing: -0.8,
            ),
          ),
          const SizedBox(height: 22),
          Container(
            padding:
                const EdgeInsets.symmetric(
              horizontal: 18,
              vertical: 12,
            ),
            decoration: BoxDecoration(
              color: Colors.white
                  .withValues(alpha: 0.16),
              borderRadius:
                  BorderRadius.circular(18),
            ),
            child: Row(
              mainAxisSize:
                  MainAxisSize.min,
              children: [
                const Icon(
                  Icons.groups_rounded,
                  color: Colors.white,
                  size: 20,
                ),
                const SizedBox(width: 10),
                Text(
                  '${households.length} nhóm đang hoạt động',
                  style: const TextStyle(
                    color: Colors.white,
                    fontWeight:
                        FontWeight.w700,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget buildEmptyState() {
    return ListView(
      padding:
          const EdgeInsets.symmetric(
        horizontal: 24,
      ),
      children: [
        const SizedBox(height: 120),
        Container(
          width: 110,
          height: 110,
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius:
                BorderRadius.circular(32),
          ),
          child: const Icon(
            Icons.account_balance_wallet,
            size: 54,
            color: AppColors.primary,
          ),
        ),
        const SizedBox(height: 28),
        const Center(
          child: Text(
            'Chưa có nhóm nào',
            style: TextStyle(
              fontSize: 24,
              fontWeight: FontWeight.w900,
              color: AppColors.textDark,
              letterSpacing: -0.5,
            ),
          ),
        ),
        const SizedBox(height: 10),
        const Center(
          child: Text(
            'Tạo nhóm đầu tiên để bắt đầu chia tiền',
            textAlign: TextAlign.center,
            style: TextStyle(
              color: AppColors.textLight,
              fontSize: 15,
              fontWeight: FontWeight.w500,
            ),
          ),
        ),
        const SizedBox(height: 28),
        ElevatedButton(
          onPressed:
              openCreateHouseholdScreen,
          child: const Text(
            'Tạo nhóm mới',
          ),
        ),
      ],
    );
  }

  Widget buildHouseholdCard(
    Household household,
  ) {
    return GestureDetector(
      onTap: () {
        Navigator.push(
          context,
          MaterialPageRoute(
            builder: (_) =>
                HouseholdDetailScreen(
              household: household,
            ),
          ),
        );
      },
      child: Container(
        margin:
            const EdgeInsets.only(
          bottom: 16,
        ),
        padding:
            const EdgeInsets.all(20),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius:
              BorderRadius.circular(26),
          boxShadow: [
            BoxShadow(
              color: Colors.black
                  .withValues(alpha: 0.03),
              blurRadius: 22,
              offset: const Offset(0, 10),
            ),
          ],
        ),
        child: Row(
          children: [
            Container(
              width: 58,
              height: 58,
              decoration: BoxDecoration(
                gradient:
                    const LinearGradient(
                  colors: [
                    AppColors.primary,
                    AppColors.secondary,
                  ],
                ),
                borderRadius:
                    BorderRadius.circular(
                  18,
                ),
              ),
              child: const Icon(
                Icons.groups_rounded,
                color: Colors.white,
              ),
            ),
            const SizedBox(width: 18),
            Expanded(
              child: Column(
                crossAxisAlignment:
                    CrossAxisAlignment
                        .start,
                children: [
                  Text(
                    household.name,
                    style:
                        const TextStyle(
                      fontSize: 18,
                      fontWeight:
                          FontWeight
                              .w800,
                      color: AppColors
                          .textDark,
                      letterSpacing:
                          -0.3,
                    ),
                  ),
                  const SizedBox(
                      height: 6),
                  Text(
                    household
                            .description
                            .isEmpty
                        ? 'Nhóm chia tiền'
                        : household
                            .description,
                    maxLines: 2,
                    overflow:
                        TextOverflow
                            .ellipsis,
                    style: const TextStyle(
                      color: AppColors
                          .textLight,
                      fontWeight:
                          FontWeight
                              .w500,
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(width: 12),
            const Icon(
              Icons.chevron_right_rounded,
              color:
                  AppColors.textLight,
            ),
          ],
        ),
      ),
    );
  }
}