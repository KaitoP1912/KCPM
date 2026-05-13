import 'package:flutter/material.dart';

import 'app_theme.dart';
import 'create_household_screen.dart';
import 'login_screen.dart';
import 'models/household.dart';
import 'services/api_service.dart';

void main() {
  runApp(const ChungViApp());
}

class ChungViApp extends StatelessWidget {
  const ChungViApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'Chung Ví',
      theme: AppTheme.lightTheme,
      home: const LoginScreen(),
    );
  }
}

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
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
      final data = await ApiService.getHouseholds();

      final loadedHouseholds = data
          .map<Household>((json) => Household.fromJson(json))
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

      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Không thể tải danh sách nhóm'),
        ),
      );
    }
  }

  Future<void> openCreateHouseholdScreen() async {
    final result = await Navigator.push(
      context,
      MaterialPageRoute(
        builder: (_) => const CreateHouseholdScreen(),
      ),
    );

    if (result == true) {
      await loadHouseholds();
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Chung Ví'),
        centerTitle: false,
      ),
      body: RefreshIndicator(
        onRefresh: loadHouseholds,
        child: isLoading
            ? const Center(
                child: CircularProgressIndicator(),
              )
            : households.isEmpty
                ? ListView(
                    children: const [
                      SizedBox(height: 120),
                      Icon(
                        Icons.account_balance_wallet_outlined,
                        size: 72,
                        color: Colors.grey,
                      ),
                      SizedBox(height: 16),
                      Center(
                        child: Text(
                          'Bạn chưa có nhóm nào',
                          style: TextStyle(
                            fontSize: 20,
                            fontWeight: FontWeight.w700,
                          ),
                        ),
                      ),
                      SizedBox(height: 8),
                      Center(
                        child: Text(
                          'Bấm nút + để tạo nhóm chia tiền đầu tiên',
                          style: TextStyle(color: Colors.grey),
                        ),
                      ),
                    ],
                  )
                : ListView.builder(
                    padding: const EdgeInsets.all(16),
                    itemCount: households.length,
                    itemBuilder: (context, index) {
                      final household = households[index];

                      return Card(
                        margin: const EdgeInsets.only(bottom: 14),
                        child: ListTile(
                          contentPadding: const EdgeInsets.all(16),
                          leading: const CircleAvatar(
                            child: Icon(Icons.groups_rounded),
                          ),
                          title: Text(
                            household.name,
                            style: const TextStyle(
                              fontWeight: FontWeight.w700,
                            ),
                          ),
                          subtitle: Padding(
                            padding: const EdgeInsets.only(top: 6),
                            child: Text(
                              household.description.isEmpty
                                  ? 'Chưa có mô tả'
                                  : household.description,
                            ),
                          ),
                          trailing: const Icon(Icons.chevron_right_rounded),
                        ),
                      );
                    },
                  ),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: openCreateHouseholdScreen,
        child: const Icon(Icons.add),
      ),
    );
  }
}