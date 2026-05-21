import 'package:flutter/material.dart';

import 'services/api_service.dart';
import 'models/household.dart';

class HouseholdMembersScreen extends StatefulWidget {
  final dynamic household;
  final String currentUserEmail;
  final ValueChanged<dynamic> onHouseholdUpdated;

  const HouseholdMembersScreen({
    super.key,
    required this.household,
    required this.currentUserEmail,
    required this.onHouseholdUpdated,
  });

  @override
  State<HouseholdMembersScreen> createState() =>
      _HouseholdMembersScreenState();
}

class _HouseholdMembersScreenState
    extends State<HouseholdMembersScreen> {
  late dynamic household;

  bool isAddingMember = false;
  bool isKickingMember = false;
  String? kickingMemberId;

  @override
  void initState() {
    super.initState();
    household = widget.household;
  }

  String getMemberId(dynamic member) {
    try {
      return member.id.toString();
    } catch (_) {
      return '';
    }
  }

  String getMemberName(dynamic member) {
    try {
      return member.displayName.toString();
    } catch (_) {
      return 'Thành viên';
    }
  }

  String getMemberEmail(dynamic member) {
    try {
      return member.userEmail.toString().toLowerCase();
    } catch (_) {
      try {
        return member.email.toString().toLowerCase();
      } catch (_) {
        return '';
      }
    }
  }

  String getMemberRole(dynamic member) {
    try {
      return member.role.toString().toLowerCase();
    } catch (_) {
      return 'member';
    }
  }

  String getMemberAvatar(dynamic member) {
    try {
      return member.userAvatar.toString();
    } catch (_) {
      return '';
    }
  }

  bool get isCurrentUserOwner {
    for (final member in household.members) {
      if (getMemberEmail(member) ==
              widget.currentUserEmail.toLowerCase() &&
          getMemberRole(member) == 'owner') {
        return true;
      }
    }

    return false;
  }

  bool canKickMember(dynamic member) {
    if (!isCurrentUserOwner) return false;

    if (getMemberEmail(member) ==
        widget.currentUserEmail.toLowerCase()) {
      return false;
    }

    if (getMemberRole(member) == 'owner') {
      return false;
    }

    return true;
  }

  Widget buildAvatar(dynamic member) {
    final avatar = getMemberAvatar(member);
    final name = getMemberName(member);

    if (avatar.isNotEmpty) {
      return CircleAvatar(
        radius: 24,
        backgroundImage: NetworkImage(avatar),
      );
    }

    return CircleAvatar(
      radius: 24,
      backgroundColor: const Color(0xFF087B63),
      child: Text(
        name.isNotEmpty ? name[0].toUpperCase() : '?',
        style: const TextStyle(
          color: Colors.white,
          fontWeight: FontWeight.w900,
          fontSize: 18,
        ),
      ),
    );
  }

  Future<void> showAddMemberDialog() async {
    final emailController = TextEditingController();

    final email = await showDialog<String>(
      context: context,
      builder: (context) {
        return AlertDialog(
          title: const Text('Thêm thành viên'),
          content: TextField(
            controller: emailController,
            keyboardType: TextInputType.emailAddress,
            decoration: const InputDecoration(
              labelText: 'Email thành viên',
              hintText: 'example@gmail.com',
            ),
          ),
          actions: [
            TextButton(
              onPressed: () {
                Navigator.pop(context);
              },
              child: const Text('Hủy'),
            ),
            ElevatedButton(
              onPressed: () {
                final value =
                    emailController.text.trim().toLowerCase();

                if (value.isEmpty || !value.contains('@')) {
                  return;
                }

                Navigator.pop(context, value);
              },
              child: const Text('Thêm'),
            ),
          ],
        );
      },
    );

    if (email == null || email.isEmpty) return;

    setState(() {
      isAddingMember = true;
    });

    try {
      final response =
          await ApiService.addMemberToHousehold(
        householdId: household.id,
        email: email,
      );

      if (!mounted) return;

      if (response['household'] != null) {
        final updatedHousehold = Household.fromJson(
          Map<String, dynamic>.from(
            response['household'],
          ),
        );

        setState(() {
          household = updatedHousehold;
        });

        widget.onHouseholdUpdated(updatedHousehold);
      }

      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Đã thêm thành viên'),
        ),
      );
    } catch (e) {
      if (!mounted) return;

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(e.toString()),
        ),
      );
    } finally {
      if (mounted) {
        setState(() {
          isAddingMember = false;
        });
      }
    }
  }

  Future<void> confirmKickMember(dynamic member) async {
    if (!canKickMember(member) || isKickingMember) return;

    final memberId = getMemberId(member);
    final memberName = getMemberName(member);
    final memberEmail = getMemberEmail(member);

    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) {
        return AlertDialog(
          title: const Text('Xóa thành viên?'),
          content: Text(
            'Bạn có chắc muốn xóa $memberName khỏi nhóm?\n\n'
            '$memberEmail\n\n'
            'Nếu thành viên còn công nợ chưa thanh toán, hệ thống sẽ không cho xóa.',
          ),
          actions: [
            TextButton(
              onPressed: () {
                Navigator.pop(context, false);
              },
              child: const Text('Hủy'),
            ),
            ElevatedButton(
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.red,
              ),
              onPressed: () {
                Navigator.pop(context, true);
              },
              child: const Text('Xóa'),
            ),
          ],
        );
      },
    );

    if (confirmed != true) return;

    setState(() {
      isKickingMember = true;
      kickingMemberId = memberId;
    });

    try {
      final response =
          await ApiService.kickMemberFromHousehold(
        householdId: household.id,
        memberId: memberId,
      );

      if (!mounted) return;

      final updatedHousehold = Household.fromJson(
        Map<String, dynamic>.from(
          response['household'],
        ),
      );

      setState(() {
        household = updatedHousehold;
      });

      widget.onHouseholdUpdated(updatedHousehold);

      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Đã xóa thành viên khỏi nhóm'),
        ),
      );
    } catch (e) {
      if (!mounted) return;

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(e.toString()),
        ),
      );
    } finally {
      if (mounted) {
        setState(() {
          isKickingMember = false;
          kickingMemberId = null;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final members = List<dynamic>.from(household.members);

    members.sort((a, b) {
      final roleA = getMemberRole(a);
      final roleB = getMemberRole(b);

      if (roleA == 'owner' && roleB != 'owner') {
        return -1;
      }

      if (roleA != 'owner' && roleB == 'owner') {
        return 1;
      }

      return getMemberName(a).compareTo(
        getMemberName(b),
      );
    });

    return Scaffold(
      backgroundColor: const Color(0xFFF4F6FA),
      appBar: AppBar(
        title: const Text('Thành viên'),
        backgroundColor: const Color(0xFFF4F6FA),
        elevation: 0,
        actions: [
          if (isCurrentUserOwner)
            IconButton(
              onPressed:
                  isAddingMember ? null : showAddMemberDialog,
              icon: isAddingMember
                  ? const SizedBox(
                      width: 20,
                      height: 20,
                      child: CircularProgressIndicator(
                        strokeWidth: 2,
                      ),
                    )
                  : const Icon(Icons.person_add_alt_1_rounded),
            ),
        ],
      ),
      body: ListView.separated(
        padding: const EdgeInsets.fromLTRB(16, 12, 16, 32),
        itemCount: members.length,
        separatorBuilder: (_, _) => const SizedBox(height: 10),
        itemBuilder: (context, index) {
          final member = members[index];
          final role = getMemberRole(member);
          final memberId = getMemberId(member);
          final isCurrentKicking =
              isKickingMember && kickingMemberId == memberId;

          return Container(
            padding: const EdgeInsets.symmetric(
              horizontal: 14,
              vertical: 12,
            ),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(18),
            ),
            child: Row(
              children: [
                buildAvatar(member),
                const SizedBox(width: 14),
                Expanded(
                  child: Column(
                    crossAxisAlignment:
                        CrossAxisAlignment.start,
                    children: [
                      Text(
                        getMemberName(member),
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                        style: const TextStyle(
                          fontSize: 15,
                          fontWeight: FontWeight.w900,
                          color: Color(0xFF111827),
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        getMemberEmail(member),
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                        style: const TextStyle(
                          fontSize: 12,
                          fontWeight: FontWeight.w600,
                          color: Color(0xFF6B7280),
                        ),
                      ),
                    ],
                  ),
                ),
                if (role == 'owner')
                  Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 10,
                      vertical: 5,
                    ),
                    decoration: BoxDecoration(
                      color: Colors.amber.withValues(alpha: 0.16),
                      borderRadius: BorderRadius.circular(999),
                    ),
                    child: const Text(
                      'Owner',
                      style: TextStyle(
                        fontSize: 11,
                        fontWeight: FontWeight.w900,
                        color: Colors.amber,
                      ),
                    ),
                  ),
                if (canKickMember(member))
                  isCurrentKicking
                      ? const Padding(
                          padding: EdgeInsets.all(12),
                          child: SizedBox(
                            width: 18,
                            height: 18,
                            child: CircularProgressIndicator(
                              strokeWidth: 2,
                            ),
                          ),
                        )
                      : PopupMenuButton<String>(
                          icon: const Icon(
                            Icons.more_horiz_rounded,
                          ),
                          onSelected: (value) {
                            if (value == 'kick') {
                              confirmKickMember(member);
                            }
                          },
                          itemBuilder: (context) => const [
                            PopupMenuItem(
                              value: 'kick',
                              child: Text(
                                'Xóa khỏi nhóm',
                                style: TextStyle(
                                  color: Colors.red,
                                  fontWeight: FontWeight.w700,
                                ),
                              ),
                            ),
                          ],
                        ),
              ],
            ),
          );
        },
      ),
    );
  }
}