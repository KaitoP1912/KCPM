class Expense {
  final String id;
  final String title;
  final double amount;
  final String note;
  final String payerName;
  final String payerEmail;
  final String createdAt;

  Expense({
    required this.id,
    required this.title,
    required this.amount,
    required this.note,
    required this.payerName,
    required this.payerEmail,
    required this.createdAt,
  });

  factory Expense.fromJson(Map<String, dynamic> json) {
    return Expense(
      id: json['id']?.toString() ?? '',
      title: json['title']?.toString() ?? 'Khoản chi',
      amount: double.tryParse(json['amount']?.toString() ?? '0') ?? 0,
      note: json['note']?.toString() ?? '',
      payerName: json['payer_name']?.toString() ?? '',
      payerEmail: json['payer_email']?.toString() ?? '',
      createdAt: json['expense_date']?.toString() ?? '',
    );
  }

  String get payerDisplayName {
    if (payerName.isNotEmpty) return payerName;
    if (payerEmail.isNotEmpty) return payerEmail;
    return 'Đang cập nhật';
  }
}