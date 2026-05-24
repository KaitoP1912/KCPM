class ExpenseParticipant {
  final String id;
  final int userId;
  final String userName;
  final String userEmail;
  final String userAvatar;
  final double shareAmount;

  ExpenseParticipant({
    required this.id,
    required this.userId,
    required this.userName,
    required this.userEmail,
    required this.userAvatar,
    required this.shareAmount,
  });

  factory ExpenseParticipant.fromJson(
    Map<String, dynamic> json,
  ) {
    return ExpenseParticipant(
      id: json['id']?.toString() ?? '',
      userId: int.tryParse(
            json['user_id']?.toString() ??
                json['user']?.toString() ??
                '',
          ) ??
          0,
      userName:
          json['user_name']?.toString() ??
              json['user_full_name']?.toString() ??
              '',
      userEmail:
          json['user_email']?.toString() ??
              json['email']?.toString() ??
              '',
      userAvatar:
          json['user_avatar']?.toString() ?? '',
      shareAmount: double.tryParse(
            json['share_amount']?.toString() ?? '0',
          ) ??
          0,
    );
  }

  String get displayName {
    if (userName.trim().isNotEmpty) {
      return userName;
    }

    return userEmail;
  }
}

class Expense {
  final String id;

  final String household;

  final String title;

  final double amount;

  final int payerId;
  final String payerName;
  final String payerEmail;
  final String payerAvatar;

  final String splitType;

  final List<ExpenseParticipant> participants;

  final String expenseDate;

  final String note;

  final bool canManage;

  final String createdAt;
  final String updatedAt;

  Expense({
    required this.id,
    required this.household,
    required this.title,
    required this.amount,
    required this.payerId,
    required this.payerName,
    required this.payerEmail,
    required this.payerAvatar,
    required this.splitType,
    required this.participants,
    required this.expenseDate,
    required this.note,
    required this.canManage,
    required this.createdAt,
    required this.updatedAt,
  });

  factory Expense.fromJson(
    Map<String, dynamic> json,
  ) {
    return Expense(
      id: json['id']?.toString() ?? '',

      household:
          json['household']?.toString() ?? '',

      title:
          json['title']?.toString() ?? '',

      amount: double.tryParse(
            json['amount']?.toString() ?? '0',
          ) ??
          0,

      payerId: int.tryParse(
            json['payer_id']?.toString() ??
                json['payer']?.toString() ??
                '',
          ) ??
          0,

      payerName:
          json['payer_name']?.toString() ?? '',

      payerEmail:
          json['payer_email']?.toString() ?? '',

      payerAvatar:
          json['payer_avatar']?.toString() ?? '',

      splitType:
          json['split_type']?.toString() ?? 'equal',

      participants: (json['participants'] as List? ?? [])
          .map(
            (item) => ExpenseParticipant.fromJson(
              Map<String, dynamic>.from(item),
            ),
          )
          .toList(),

      expenseDate:
          json['expense_date']?.toString() ?? '',

      note:
          json['note']?.toString() ?? '',

      canManage:
          json['can_manage'] == true,

      createdAt:
          json['created_at']?.toString() ?? '',

      updatedAt:
          json['updated_at']?.toString() ?? '',
    );
  }

  String get displayPayer {
    if (payerName.trim().isNotEmpty) {
      return payerName;
    }

    return payerEmail;
  }

  bool get isEqualSplit {
    return splitType == 'equal';
  }
}
