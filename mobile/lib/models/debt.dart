class Debt {
  final String id;
  final double amount;
  final String fromUserName;
  final String fromUserEmail;
  final String toUserName;
  final String toUserEmail;
  final bool isSettled;

  Debt({
    required this.id,
    required this.amount,
    required this.fromUserName,
    required this.fromUserEmail,
    required this.toUserName,
    required this.toUserEmail,
    required this.isSettled,
  });

  factory Debt.fromJson(Map<String, dynamic> json) {
    return Debt(
      id: json['id']?.toString() ?? '',
      amount: double.tryParse(json['amount']?.toString() ?? '0') ?? 0,
      fromUserName: json['from_user_name']?.toString() ?? '',
      fromUserEmail: json['from_user_email']?.toString() ?? '',
      toUserName: json['to_user_name']?.toString() ?? '',
      toUserEmail: json['to_user_email']?.toString() ?? '',
      isSettled: json['is_paid'] == true,
    );
  }

  String get fromDisplayName {
    if (fromUserName.isNotEmpty) return fromUserName;
    if (fromUserEmail.isNotEmpty) return fromUserEmail;
    return 'Người dùng';
  }

  String get toDisplayName {
    if (toUserName.isNotEmpty) return toUserName;
    if (toUserEmail.isNotEmpty) return toUserEmail;
    return 'Người dùng';
  }
}