import 'package:flutter/material.dart';

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
      theme: ThemeData(
        primarySwatch: Colors.green,
      ),
      home: const HomeScreen(),
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
    try {
      final data = await ApiService.getHouseholds();

      households = data
          .map<Household>((json) => Household.fromJson(json))
          .toList();

      setState(() {
        isLoading = false;
      });
    } catch (e) {
      print(e);

      setState(() {
        isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Chung Ví"),
      ),
      body: isLoading
          ? const Center(
              child: CircularProgressIndicator(),
            )
          : ListView.builder(
              itemCount: households.length,
              itemBuilder: (context, index) {
                final household = households[index];

                return Card(
                  margin: const EdgeInsets.all(12),
                  child: ListTile(
                    leading: const CircleAvatar(
                      child: Icon(Icons.home),
                    ),
                    title: Text(household.name),
                    subtitle: Text(household.description),
                  ),
                );
              },
            ),
    );
  }
}