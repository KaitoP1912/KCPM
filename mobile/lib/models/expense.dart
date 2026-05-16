class Expense {
  final String id;

  final String title;

  final double amount;

  final String payerName;
  final String payerEmail;
  final String payerAvatar;

  final String expenseDate;

  final String note;

  Expense({
    required this.id,
    required this.title,
    required this.amount,
    required this.payerName,
    required this.payerEmail,
    required this.payerAvatar,
    required this.expenseDate,
    required this.note,
  });

  factory Expense.fromJson(
    Map<String, dynamic> json,
  ) {
    return Expense(
      id: json['id'].toString(),

      title:
          json['title']?.toString() ?? '',

      amount: double.tryParse(
            json['amount'].toString(),
          ) ??
          0,

      payerName:
          json['payer_name']?.toString() ?? '',

      payerEmail:
          json['payer_email']?.toString() ?? '',

      payerAvatar:
          json['payer_avatar']?.toString() ?? '',

      expenseDate:
          json['expense_date']?.toString() ?? '',

      note:
          json['note']?.toString() ?? '',
    );
  }

  String get displayPayer {
    if (payerName.trim().isNotEmpty) {
      return payerName;
    }

    return payerEmail;
  }
}