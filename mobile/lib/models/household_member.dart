class HouseholdMember {
  final String id;

  final int user;

  final String userEmail;
  final String userFullName;
  final String userAvatar;

  final String role;

  HouseholdMember({
    required this.id,
    required this.user,
    required this.userEmail,
    required this.userFullName,
    required this.userAvatar,
    required this.role,
  });

  factory HouseholdMember.fromJson(
    Map<String, dynamic> json,
  ) {
    return HouseholdMember(
      id: json['id'].toString(),

      user: json['user'] ?? 0,

      userEmail:
          json['user_email']?.toString() ?? '',

      userFullName:
          json['user_full_name']?.toString() ?? '',

      userAvatar:
          json['user_avatar']?.toString() ?? '',

      role:
          json['role']?.toString() ?? '',
    );
  }

  String get displayName {
    if (userFullName.trim().isNotEmpty) {
      return userFullName;
    }

    return userEmail;
  }
}