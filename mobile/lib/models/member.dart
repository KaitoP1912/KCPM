class HouseholdMember {
  final String id;
  final int user;

  final String email;
  final String fullName;
  final String userAvatar;

  final String role;

  HouseholdMember({
    required this.id,
    required this.user,
    required this.email,
    required this.fullName,
    required this.userAvatar,
    required this.role,
  });

  factory HouseholdMember.fromJson(Map<String, dynamic> json) {
    return HouseholdMember(
      id: json['id']?.toString() ?? '',
      user: json['user'] ?? 0,
      email: json['user_email']?.toString() ??
          json['email']?.toString() ??
          '',
      fullName: json['user_full_name']?.toString() ??
          json['full_name']?.toString() ??
          '',
      userAvatar: json['user_avatar']?.toString() ?? '',
      role: json['role']?.toString() ?? 'member',
    );
  }

  String get displayName {
    if (fullName.trim().isNotEmpty) {
      return fullName;
    }

    return email;
  }
}