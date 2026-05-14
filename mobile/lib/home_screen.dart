import 'package:flutter/material.dart';

import 'app_theme.dart';
import 'create_household_screen.dart';
import 'household_detail_screen.dart';
import 'models/household.dart';
import 'services/api_service.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HouseholdDebtResult {
  final String householdId;
  final List<dynamic> debts;

  _HouseholdDebtResult({
    required this.householdId,
    required this.debts,
  });
}

class _HomeScreenState extends State<HomeScreen> {
  bool isLoading = true;

  List<Household> households = [];
  List<Household> filteredHouseholds = [];

  final searchController = TextEditingController();

  String currentEmail = '';

  double totalOwe = 0;
  double totalReceive = 0;

  final Map<String, double> groupOweMap = {};
  final Map<String, double> groupReceiveMap = {};

  @override
  void initState() {
    super.initState();
    searchController.addListener(filterHouseholds);
    loadData();
  }

  @override
  void dispose() {
    searchController.dispose();
    super.dispose();
  }

  Future<void> loadData() async {
    try {
      setState(() => isLoading = true);

      final savedEmail = await ApiService.getSavedEmail();
      currentEmail = savedEmail ?? '';

      final householdData = await ApiService.getHouseholds();

      final loadedHouseholds = householdData
          .map<Household>(
            (json) => Household.fromJson(
              Map<String, dynamic>.from(json),
            ),
          )
          .toList();

      final debtResults = await Future.wait(
        loadedHouseholds.map((household) async {
          try {
            final debts = await ApiService.getHouseholdDebts(household.id);

            return _HouseholdDebtResult(
              householdId: household.id,
              debts: debts,
            );
          } catch (_) {
            return _HouseholdDebtResult(
              householdId: household.id,
              debts: [],
            );
          }
        }),
      );

      double owe = 0;
      double receive = 0;

      groupOweMap.clear();
      groupReceiveMap.clear();

      final me = currentEmail.toLowerCase();

      for (final result in debtResults) {
        double groupOwe = 0;
        double groupReceive = 0;

        for (final item in result.debts) {
          final debt = Map<String, dynamic>.from(item);

          final amount = double.tryParse(
                debt['amount']?.toString() ?? '0',
              ) ??
              0;

          final fromEmail =
              debt['from_user_email']?.toString().toLowerCase() ?? '';

          final toEmail =
              debt['to_user_email']?.toString().toLowerCase() ?? '';

          if (fromEmail == me) {
            owe += amount;
            groupOwe += amount;
          }

          if (toEmail == me) {
            receive += amount;
            groupReceive += amount;
          }
        }

        groupOweMap[result.householdId] = groupOwe;
        groupReceiveMap[result.householdId] = groupReceive;
      }

      if (!mounted) return;

      setState(() {
        households = loadedHouseholds;
        filteredHouseholds = loadedHouseholds;
        totalOwe = owe;
        totalReceive = receive;
        isLoading = false;
      });
    } catch (e) {
      debugPrint(e.toString());

      if (!mounted) return;

      setState(() => isLoading = false);

      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Không thể tải dữ liệu trang chủ'),
        ),
      );
    }
  }

  void filterHouseholds() {
    final keyword = searchController.text.trim().toLowerCase();

    if (keyword.isEmpty) {
      setState(() {
        filteredHouseholds = households;
      });
      return;
    }

    setState(() {
      filteredHouseholds = households.where((household) {
        return household.name.toLowerCase().contains(keyword) ||
            household.description.toLowerCase().contains(keyword);
      }).toList();
    });
  }

  String formatMoney(double amount) {
    return amount.toStringAsFixed(0).replaceAllMapped(
          RegExp(r'\B(?=(\d{3})+(?!\d))'),
          (match) => '.',
        );
  }

  Future<void> openCreateHousehold() async {
    await Navigator.push(
      context,
      MaterialPageRoute(
        builder: (_) => const CreateHouseholdScreen(),
      ),
    );

    await loadData();
  }

  Widget buildHeader() {
    return Row(
      children: [
        Container(
          width: 58,
          height: 58,
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(20),
            gradient: const LinearGradient(
              colors: [
                AppColors.primary,
                AppColors.secondary,
              ],
            ),
          ),
          child: Padding(
            padding: const EdgeInsets.all(10),
            child: Image.asset(
              'assets/images/logo.png',
            ),
          ),
        ),
        const SizedBox(width: 14),
        const Expanded(
          child: Column(
            crossAxisAlignment:
                CrossAxisAlignment.start,
            children: [
              Text(
                'Chung Ví',
                style: TextStyle(
                  color: AppColors.textDark,
                  fontSize: 28,
                  fontWeight: FontWeight.w900,
                  letterSpacing: -0.8,
                  height: 1,
                ),
              ),
              SizedBox(height: 6),
              Text(
                'Quản lý chi tiêu nhóm',
                style: TextStyle(
                  color: AppColors.textLight,
                  fontSize: 14,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ],
          ),
        ),
        Container(
          width: 46,
          height: 46,
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius:
                BorderRadius.circular(16),
          ),
          child: const Icon(
            Icons.notifications_none_rounded,
            color: AppColors.textDark,
          ),
        ),
      ],
    );
  }

  Widget buildSummaryCard() {
    final netBalance = totalReceive - totalOwe;

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
          const Text(
            'Tổng công nợ',
            style: TextStyle(
              color: Colors.white70,
              fontSize: 15,
              fontWeight: FontWeight.w700,
            ),
          ),
          const SizedBox(height: 10),
          Text(
            '${formatMoney(netBalance)}đ',
            style: const TextStyle(
              color: Colors.white,
              fontSize: 38,
              fontWeight: FontWeight.w900,
              letterSpacing: -1,
            ),
          ),
          const SizedBox(height: 26),
          Row(
            children: [
              buildMoneyBox(
                title: 'Bạn đang nợ',
                amount: totalOwe,
                icon: Icons.arrow_upward_rounded,
              ),
              const SizedBox(width: 12),
              buildMoneyBox(
                title: 'Bạn sẽ nhận',
                amount: totalReceive,
                icon: Icons.arrow_downward_rounded,
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget buildMoneyBox({
    required String title,
    required double amount,
    required IconData icon,
  }) {
    return Expanded(
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: Colors.white.withValues(alpha: 0.14),
          borderRadius: BorderRadius.circular(20),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Icon(
              icon,
              color: Colors.white,
              size: 22,
            ),
            const SizedBox(height: 14),
            Text(
              title,
              style: const TextStyle(
                color: Colors.white70,
                fontWeight: FontWeight.w700,
              ),
            ),
            const SizedBox(height: 6),
            Text(
              '${formatMoney(amount)}đ',
              style: const TextStyle(
                color: Colors.white,
                fontSize: 19,
                fontWeight: FontWeight.w900,
                letterSpacing: -0.3,
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
        prefixIcon: const Icon(Icons.search_rounded),
        suffixIcon: searchController.text.isNotEmpty
            ? IconButton(
                onPressed: () => searchController.clear(),
                icon: const Icon(Icons.close_rounded),
              )
            : null,
      ),
    );
  }

  Widget buildSectionTitle() {
    return Row(
      children: [
        const Text(
          'Danh sách nhóm',
          style: TextStyle(
            color: AppColors.textDark,
            fontSize: 22,
            fontWeight: FontWeight.w900,
            letterSpacing: -0.5,
          ),
        ),
        const Spacer(),
        Text(
          '${filteredHouseholds.length}',
          style: const TextStyle(
            color: AppColors.textLight,
            fontWeight: FontWeight.w800,
          ),
        ),
      ],
    );
  }

  Widget buildHouseholdCard(Household household) {
    final groupOwe = groupOweMap[household.id] ?? 0;
    final groupReceive = groupReceiveMap[household.id] ?? 0;

    String statusText = 'Không có công nợ';
    Color statusColor = AppColors.success;
    IconData statusIcon = Icons.check_circle_rounded;

    if (groupOwe > 0) {
      statusText = 'Bạn đang nợ: ${formatMoney(groupOwe)}đ';
      statusColor = AppColors.danger;
      statusIcon = Icons.arrow_upward_rounded;
    } else if (groupReceive > 0) {
      statusText = 'Bạn sẽ nhận: ${formatMoney(groupReceive)}đ';
      statusColor = AppColors.success;
      statusIcon = Icons.arrow_downward_rounded;
    }

    return GestureDetector(
      onTap: () async {
        await Navigator.push(
          context,
          MaterialPageRoute(
            builder: (_) => HouseholdDetailScreen(
              household: household,
            ),
          ),
        );

        await loadData();
      },
      child: Container(
        margin: const EdgeInsets.only(bottom: 16),
        padding: const EdgeInsets.all(18),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(26),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withValues(alpha: 0.03),
              blurRadius: 20,
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
                gradient: const LinearGradient(
                  colors: [
                    AppColors.primary,
                    AppColors.secondary,
                  ],
                ),
                borderRadius: BorderRadius.circular(20),
              ),
              child: const Icon(
                Icons.home_rounded,
                color: Colors.white,
                size: 28,
              ),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    household.name,
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: const TextStyle(
                      color: AppColors.textDark,
                      fontSize: 18,
                      fontWeight: FontWeight.w900,
                      letterSpacing: -0.4,
                    ),
                  ),
                  const SizedBox(height: 6),
                  Text(
                    '${household.members.length} thành viên',
                    style: const TextStyle(
                      color: AppColors.textLight,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  const SizedBox(height: 10),
                  Row(
                    children: [
                      Icon(
                        statusIcon,
                        color: statusColor,
                        size: 18,
                      ),
                      const SizedBox(width: 6),
                      Expanded(
                        child: Text(
                          statusText,
                          overflow: TextOverflow.ellipsis,
                          style: TextStyle(
                            color: statusColor,
                            fontWeight: FontWeight.w800,
                          ),
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
            const SizedBox(width: 12),
            const Icon(
              Icons.chevron_right_rounded,
              color: AppColors.textLight,
            ),
          ],
        ),
      ),
    );
  }

  Widget buildEmptyState() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(34),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(32),
      ),
      child: Column(
        children: [
          Container(
            width: 84,
            height: 84,
            decoration: BoxDecoration(
              gradient: const LinearGradient(
                colors: [
                  AppColors.primary,
                  AppColors.secondary,
                ],
              ),
              borderRadius: BorderRadius.circular(28),
            ),
            child: const Icon(
              Icons.groups_rounded,
              color: Colors.white,
              size: 42,
            ),
          ),
          const SizedBox(height: 24),
          const Text(
            'Chưa có nhóm nào',
            style: TextStyle(
              color: AppColors.textDark,
              fontSize: 22,
              fontWeight: FontWeight.w900,
            ),
          ),
          const SizedBox(height: 12),
          const Text(
            'Tạo nhóm đầu tiên để bắt đầu chia tiền cùng mọi người.',
            textAlign: TextAlign.center,
            style: TextStyle(
              color: AppColors.textLight,
              fontWeight: FontWeight.w600,
              height: 1.5,
            ),
          ),
          const SizedBox(height: 28),
          ElevatedButton(
            onPressed: openCreateHousehold,
            child: const Text('Tạo nhóm ngay'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      floatingActionButton: FloatingActionButton(
        elevation: 0,
        backgroundColor: AppColors.primary,
        onPressed: openCreateHousehold,
        child: const Icon(
          Icons.add_rounded,
          color: Colors.white,
          size: 30,
        ),
      ),
      body: SafeArea(
        child: isLoading
            ? const Center(
                child: CircularProgressIndicator(),
              )
            : RefreshIndicator(
                onRefresh: loadData,
                child: ListView(
                  padding: const EdgeInsets.all(20),
                  children: [
                    buildHeader(),
                    const SizedBox(height: 26),
                    buildSummaryCard(),
                    const SizedBox(height: 24),
                    buildSearchBar(),
                    const SizedBox(height: 28),
                    buildSectionTitle(),
                    const SizedBox(height: 16),
                    if (filteredHouseholds.isEmpty)
                      buildEmptyState()
                    else
                      ...filteredHouseholds.map(buildHouseholdCard),
                    const SizedBox(height: 120),
                  ],
                ),
              ),
      ),
    );
  }
}