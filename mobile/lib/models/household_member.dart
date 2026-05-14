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
      user: json['user'] is int
          ? json['user']
          : int.tryParse(json['user']?.toString() ?? '0') ?? 0,
      email: json['user_email']?.toString() ??
          json['email']?.toString() ??
          '',
      fullName: json['user_full_name']?.toString() ??
          json['full_name']?.toString() ??
          '',
      role: json['role']?.toString() ?? 'member',
    );
  }
}