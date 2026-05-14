import 'package:flutter/material.dart';

import 'add_expense_screen.dart';
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
  bool isLoading = true;

  List<Household> households = [];
  List<Household> filteredHouseholds =
      [];

  final searchController =
      TextEditingController();

  @override
  void initState() {
    super.initState();

    loadHouseholds();

    searchController.addListener(
      filterHouseholds,
    );
  }

  @override
  void dispose() {
    searchController.dispose();
    super.dispose();
  }

  Future<void> loadHouseholds() async {
    try {
      setState(() {
        isLoading = true;
      });

      final data =
          await ApiService.getHouseholds();

      final loadedHouseholds = data
          .map<Household>(
            (json) => Household.fromJson(
              Map<String, dynamic>.from(
                json,
              ),
            ),
          )
          .toList();

      if (!mounted) return;

      setState(() {
        households = loadedHouseholds;
        filteredHouseholds =
            loadedHouseholds;
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
            'Không thể tải nhóm',
          ),
        ),
      );
    }
  }

  void filterHouseholds() {
    final keyword =
        searchController.text
            .trim()
            .toLowerCase();

    if (keyword.isEmpty) {
      setState(() {
        filteredHouseholds =
            households;
      });

      return;
    }

    setState(() {
      filteredHouseholds =
          households.where((household) {
        return household.name
                .toLowerCase()
                .contains(keyword) ||
            household.description
                .toLowerCase()
                .contains(keyword);
      }).toList();
    });
  }

  String getGreeting() {
    final hour =
        DateTime.now().hour;

    if (hour < 12) {
      return 'Chào buổi sáng ☀️';
    }

    if (hour < 18) {
      return 'Chào buổi chiều 👋';
    }

    return 'Chào buổi tối 🌙';
  }

  String formatMoney(double amount) {
    return amount
        .toStringAsFixed(0)
        .replaceAllMapped(
          RegExp(
            r'\B(?=(\d{3})+(?!\d))',
          ),
          (match) => '.',
        );
  }

  int getTotalMembers() {
    int total = 0;

    for (final household
        in households) {
      total +=
          household.members.length;
    }

    return total;
  }

  Widget buildHeader() {
    return Row(
      children: [
        Expanded(
          child: Column(
            crossAxisAlignment:
                CrossAxisAlignment.start,
            children: [
              Text(
                getGreeting(),
                style: const TextStyle(
                  color:
                      AppColors.textLight,
                  fontWeight:
                      FontWeight.w700,
                  fontSize: 15,
                ),
              ),
              const SizedBox(height: 8),
              const Text(
                'Quản lý chi tiêu nhóm\ndễ dàng hơn',
                style: TextStyle(
                  fontSize: 30,
                  fontWeight:
                      FontWeight.w900,
                  height: 1.1,
                  letterSpacing: -1,
                  color:
                      AppColors.textDark,
                ),
              ),
            ],
          ),
        ),
        Container(
          width: 60,
          height: 60,
          decoration: BoxDecoration(
            borderRadius:
                BorderRadius.circular(
              20,
            ),
            gradient:
                const LinearGradient(
              colors: [
                AppColors.primary,
                AppColors.secondary,
              ],
            ),
          ),
          child: Padding(
            padding:
                const EdgeInsets.all(10),
            child: Image.asset(
              'assets/images/logo.png',
            ),
          ),
        ),
      ],
    );
  }

  Widget buildAnalyticsCard() {
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
            BorderRadius.circular(32),
      ),
      child: Column(
        crossAxisAlignment:
            CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                width: 56,
                height: 56,
                decoration: BoxDecoration(
                  color: Colors.white
                      .withValues(
                    alpha: 0.16,
                  ),
                  borderRadius:
                      BorderRadius
                          .circular(
                    18,
                  ),
                ),
                child: const Icon(
                  Icons.account_balance_wallet_rounded,
                  color:
                      Colors.white,
                  size: 28,
                ),
              ),
              const Spacer(),
              Container(
                padding:
                    const EdgeInsets
                        .symmetric(
                  horizontal: 14,
                  vertical: 10,
                ),
                decoration:
                    BoxDecoration(
                  color: Colors.white
                      .withValues(
                    alpha: 0.14,
                  ),
                  borderRadius:
                      BorderRadius
                          .circular(
                    16,
                  ),
                ),
                child: const Row(
                  children: [
                    Icon(
                      Icons.trending_up_rounded,
                      color:
                          Colors.white,
                      size: 18,
                    ),
                    SizedBox(
                        width: 8),
                    Text(
                      'Đang hoạt động',
                      style:
                          TextStyle(
                        color: Colors
                            .white,
                        fontWeight:
                            FontWeight
                                .w700,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 30),
          const Text(
            'Tổng số nhóm',
            style: TextStyle(
              color: Colors.white70,
              fontWeight:
                  FontWeight.w600,
            ),
          ),
          const SizedBox(height: 10),
          Text(
            '${households.length}',
            style: const TextStyle(
              color: Colors.white,
              fontSize: 42,
              fontWeight:
                  FontWeight.w900,
              letterSpacing: -1,
            ),
          ),
          const SizedBox(height: 24),
          Row(
            children: [
              buildMiniStat(
                icon:
                    Icons.groups_rounded,
                value:
                    '${getTotalMembers()}',
                label:
                    'Thành viên',
              ),
              const SizedBox(width: 12),
              buildMiniStat(
                icon:
                    Icons.receipt_long_rounded,
                value:
                    '${households.length}',
                label: 'Nhóm',
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget buildMiniStat({
    required IconData icon,
    required String value,
    required String label,
  }) {
    return Expanded(
      child: Container(
        padding:
            const EdgeInsets.all(
          16,
        ),
        decoration: BoxDecoration(
          color: Colors.white
              .withValues(
            alpha: 0.12,
          ),
          borderRadius:
              BorderRadius.circular(
            20,
          ),
        ),
        child: Column(
          crossAxisAlignment:
              CrossAxisAlignment.start,
          children: [
            Icon(
              icon,
              color: Colors.white,
              size: 22,
            ),
            const SizedBox(height: 14),
            Text(
              value,
              style:
                  const TextStyle(
                color: Colors.white,
                fontSize: 24,
                fontWeight:
                    FontWeight.w900,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              label,
              style:
                  const TextStyle(
                color:
                    Colors.white70,
                fontWeight:
                    FontWeight.w600,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget buildSearchBar() {
    return TextField(
      controller: searchController,
      style: const TextStyle(
        fontWeight: FontWeight.w700,
      ),
      decoration: InputDecoration(
        hintText: 'Tìm nhóm...',
        prefixIcon: const Icon(
          Icons.search_rounded,
        ),
        suffixIcon:
            searchController
                    .text
                    .isNotEmpty
                ? IconButton(
                    onPressed: () {
                      searchController
                          .clear();
                    },
                    icon: const Icon(
                      Icons.close_rounded,
                    ),
                  )
                : null,
      ),
    );
  }

  Widget buildSectionTitle(
    String title,
  ) {
    return Row(
      children: [
        Text(
          title,
          style: const TextStyle(
            fontSize: 22,
            fontWeight:
                FontWeight.w900,
            letterSpacing: -0.5,
            color:
                AppColors.textDark,
          ),
        ),
        const Spacer(),
        Text(
          '${filteredHouseholds.length}',
          style: const TextStyle(
            color:
                AppColors.textLight,
            fontWeight:
                FontWeight.w700,
          ),
        ),
      ],
    );
  }

  Widget buildHouseholdCard(
    Household household,
  ) {
    return GestureDetector(
      onTap: () async {
        await Navigator.push(
          context,
          MaterialPageRoute(
            builder: (_) =>
                HouseholdDetailScreen(
              household: household,
            ),
          ),
        );

        await loadHouseholds();
      },
      child: Container(
        margin:
            const EdgeInsets.only(
          bottom: 18,
        ),
        padding:
            const EdgeInsets.all(
          20,
        ),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius:
              BorderRadius.circular(
            28,
          ),
          boxShadow: [
            BoxShadow(
              color: Colors.black
                  .withValues(
                alpha: 0.03,
              ),
              blurRadius: 20,
              offset:
                  const Offset(
                0,
                10,
              ),
            ),
          ],
        ),
        child: Column(
          children: [
            Row(
              children: [
                Container(
                  width: 58,
                  height: 58,
                  decoration:
                      BoxDecoration(
                    gradient:
                        const LinearGradient(
                      colors: [
                        AppColors
                            .primary,
                        AppColors
                            .secondary,
                      ],
                    ),
                    borderRadius:
                        BorderRadius
                            .circular(
                      20,
                    ),
                  ),
                  child: const Icon(
                    Icons
                        .groups_rounded,
                    color:
                        Colors.white,
                    size: 28,
                  ),
                ),
                const SizedBox(
                    width: 16),
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
                          fontSize:
                              18,
                          fontWeight:
                              FontWeight
                                  .w900,
                          color:
                              AppColors
                                  .textDark,
                          letterSpacing:
                              -0.4,
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
                        maxLines: 1,
                        overflow:
                            TextOverflow
                                .ellipsis,
                        style:
                            const TextStyle(
                          color:
                              AppColors
                                  .textLight,
                          fontWeight:
                              FontWeight
                                  .w600,
                        ),
                      ),
                    ],
                  ),
                ),
                const Icon(
                  Icons
                      .arrow_forward_ios_rounded,
                  size: 18,
                  color:
                      AppColors.textLight,
                ),
              ],
            ),
            const SizedBox(height: 22),
            Row(
              children: [
                buildInfoChip(
                  icon:
                      Icons.people_alt_rounded,
                  label:
                      '${household.members.length} thành viên',
                ),
                const SizedBox(
                    width: 10),
                buildInfoChip(
                  icon:
                      Icons.schedule_rounded,
                  label:
                      'Đang hoạt động',
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget buildInfoChip({
    required IconData icon,
    required String label,
  }) {
    return Container(
      padding:
          const EdgeInsets.symmetric(
        horizontal: 14,
        vertical: 10,
      ),
      decoration: BoxDecoration(
        color: AppColors
            .primary
            .withValues(
          alpha: 0.08,
        ),
        borderRadius:
            BorderRadius.circular(
          16,
        ),
      ),
      child: Row(
        children: [
          Icon(
            icon,
            size: 18,
            color: AppColors.primary,
          ),
          const SizedBox(width: 8),
          Text(
            label,
            style: const TextStyle(
              color:
                  AppColors.primary,
              fontWeight:
                  FontWeight.w700,
            ),
          ),
        ],
      ),
    );
  }

  Widget buildEmptyState() {
    return Container(
      width: double.infinity,
      padding:
          const EdgeInsets.all(34),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius:
            BorderRadius.circular(
          32,
        ),
      ),
      child: Column(
        children: [
          Container(
            width: 84,
            height: 84,
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
                28,
              ),
            ),
            child: const Icon(
              Icons
                  .groups_rounded,
              color: Colors.white,
              size: 42,
            ),
          ),
          const SizedBox(height: 24),
          const Text(
            'Chưa có nhóm nào',
            style: TextStyle(
              fontSize: 22,
              fontWeight:
                  FontWeight.w900,
              color:
                  AppColors.textDark,
            ),
          ),
          const SizedBox(height: 12),
          const Text(
            'Tạo nhóm đầu tiên để bắt đầu chia chi tiêu cùng bạn bè',
            textAlign:
                TextAlign.center,
            style: TextStyle(
              color:
                  AppColors.textLight,
              fontWeight:
                  FontWeight.w600,
              height: 1.5,
            ),
          ),
          const SizedBox(height: 28),
          SizedBox(
            width: double.infinity,
            height: 56,
            child: ElevatedButton(
              onPressed: () async {
                await Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (_) =>
                        const CreateHouseholdScreen(),
                  ),
                );

                await loadHouseholds();
              },
              child: const Text(
                'Tạo nhóm ngay',
              ),
            ),
          ),
        ],
      ),
    );
  }

  Future<void> openCreateHousehold() async {
    await Navigator.push(
      context,
      MaterialPageRoute(
        builder: (_) =>
            const CreateHouseholdScreen(),
      ),
    );

    await loadHouseholds();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor:
          AppColors.background,
      floatingActionButton:
          FloatingActionButton(
        elevation: 0,
        backgroundColor:
            AppColors.primary,
        onPressed:
            openCreateHousehold,
        child: const Icon(
          Icons.add_rounded,
          color: Colors.white,
          size: 30,
        ),
      ),
      body: SafeArea(
        child: isLoading
            ? const Center(
                child:
                    CircularProgressIndicator(),
              )
            : RefreshIndicator(
                onRefresh:
                    loadHouseholds,
                child: ListView(
                  padding:
                      const EdgeInsets.all(
                    20,
                  ),
                  children: [
                    buildHeader(),
                    const SizedBox(
                        height: 28),
                    buildAnalyticsCard(),
                    const SizedBox(
                        height: 26),
                    buildSearchBar(),
                    const SizedBox(
                        height: 30),
                    buildSectionTitle(
                      'Nhóm của bạn',
                    ),
                    const SizedBox(
                        height: 18),
                    if (filteredHouseholds
                        .isEmpty)
                      buildEmptyState()
                    else
                      ...filteredHouseholds
                          .map(
                        buildHouseholdCard,
                      ),
                    const SizedBox(
                        height: 120),
                  ],
                ),
              ),
      ),
    );
  }
}