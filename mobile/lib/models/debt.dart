class Debt {
  final String id;

  final String fromUserName;
  final String fromUserEmail;
  final String fromUserAvatar;

  final String toUserName;
  final String toUserEmail;
  final String toUserAvatar;

  final String bankName;
  final String bankAccountNumber;
  final String bankAccountHolder;

  final double amount;

  final bool isPaid;

  Debt({
    required this.id,
    required this.fromUserName,
    required this.fromUserEmail,
    required this.fromUserAvatar,
    required this.toUserName,
    required this.toUserEmail,
    required this.toUserAvatar,
    required this.bankName,
    required this.bankAccountNumber,
    required this.bankAccountHolder,
    required this.amount,
    required this.isPaid,
  });

  factory Debt.fromJson(
    Map<String, dynamic> json,
  ) {
    return Debt(
      id: json['id'].toString(),

      fromUserName:
          json['from_user_name']?.toString() ?? '',

      fromUserEmail:
          json['from_user_email']?.toString() ?? '',

      fromUserAvatar:
          json['from_user_avatar']?.toString() ?? '',

      toUserName:
          json['to_user_name']?.toString() ?? '',

      toUserEmail:
          json['to_user_email']?.toString() ?? '',

      toUserAvatar:
          json['to_user_avatar']?.toString() ?? '',

      bankName:
          json['bank_name']?.toString() ?? '',

      bankAccountNumber:
          json['bank_account_number']?.toString() ?? '',

      bankAccountHolder:
          json['bank_account_holder']?.toString() ?? '',

      amount: double.tryParse(
            json['amount'].toString(),
          ) ??
          0,

      isPaid:
          json['is_paid'] ?? false,
    );
  }
}