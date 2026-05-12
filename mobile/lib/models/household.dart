class Household {
  final String id;
  final String name;
  final String description;

  Household({
    required this.id,
    required this.name,
    required this.description,
  });

  factory Household.fromJson(Map<String, dynamic> json) {
    return Household(
      id: json['id'],
      name: json['name'] ?? '',
      description: json['description'] ?? '',
    );
  }
}