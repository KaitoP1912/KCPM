import 'member.dart';

class Household {
  final String id;
  final String name;
  final String description;
  final List<HouseholdMember> members;

  Household({
    required this.id,
    required this.name,
    required this.description,
    required this.members,
  });

  factory Household.fromJson(Map<String, dynamic> json) {
    return Household(
      id: json['id']?.toString() ?? '',
      name: json['name'] ?? '',
      description: json['description'] ?? '',
      members: (json['members'] as List? ?? [])
          .map((item) => HouseholdMember.fromJson(item))
          .toList(),
    );
  }
}