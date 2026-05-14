class HouseholdMember {
  final String id;
  final int user;
  final String email;
  final String fullName;
  final String role;

  HouseholdMember({
    required this.id,
    required this.user,
    required this.email,
    required this.fullName,
    required this.role,
  });

  factory HouseholdMember.fromJson(Map<String, dynamic> json) {
    return HouseholdMember(
      id: json['id']?.toString() ?? '',
      user: json['user'] ?? 0,
      email: json['user_email'] ?? json['email'] ?? '',
      fullName: json['user_full_name'] ?? json['full_name'] ?? '',
      role: json['role'] ?? 'member',
    );
  }

  String get displayName {
    if (fullName.trim().isNotEmpty) return fullName;
    return email;
  }
}