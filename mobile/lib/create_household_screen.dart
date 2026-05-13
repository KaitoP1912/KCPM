import 'package:flutter/material.dart';

import 'services/api_service.dart';

class CreateHouseholdScreen extends StatefulWidget {
  const CreateHouseholdScreen({super.key});

  @override
  State<CreateHouseholdScreen> createState() =>
      _CreateHouseholdScreenState();
}

class _CreateHouseholdScreenState
    extends State<CreateHouseholdScreen> {
  final nameController = TextEditingController();
  final descriptionController = TextEditingController();

  bool isLoading = false;

  Future<void> createHousehold() async {
    try {
      setState(() {
        isLoading = true;
      });

      await ApiService.createHousehold(
        name: nameController.text,
        description: descriptionController.text,
      );

      if (!mounted) return;

      Navigator.pop(context, true);
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text("Tạo nhóm thất bại"),
        ),
      );
    }

    setState(() {
      isLoading = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Tạo nhóm"),
      ),
      body: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          children: [
            TextField(
              controller: nameController,
              decoration: const InputDecoration(
                hintText: "Tên nhóm",
              ),
            ),

            const SizedBox(height: 20),

            TextField(
              controller: descriptionController,
              decoration: const InputDecoration(
                hintText: "Mô tả",
              ),
            ),

            const SizedBox(height: 30),

            SizedBox(
              width: double.infinity,
              height: 56,
              child: ElevatedButton(
                onPressed: isLoading
                    ? null
                    : createHousehold,
                child: isLoading
                    ? const CircularProgressIndicator(
                        color: Colors.white,
                      )
                    : const Text("Tạo nhóm"),
              ),
            ),
          ],
        ),
      ),
    );
  }
}