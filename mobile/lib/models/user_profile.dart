class UserProfile {
  final String? id;
  final String name;
  final int age;
  final String gender;
  final String landHolding;
  final String crop;
  final String caste;
  final String income;
  final DateTime createdAt;

  UserProfile({
    this.id,
    required this.name,
    required this.age,
    required this.gender,
    required this.landHolding,
    required this.crop,
    required this.caste,
    required this.income,
    DateTime? createdAt,
  }) : createdAt = createdAt ?? DateTime.now();

  Map<String, dynamic> toJson() {
    return {
      'name': name,
      'age': age,
      'gender': gender,
      'landHolding': landHolding,
      'crop': crop,
      'caste': caste,
      'income': income,
      'createdAt': createdAt.toIso8601String(),
    };
  }

  factory UserProfile.fromJson(Map<String, dynamic> json, String id) {
    return UserProfile(
      id: id,
      name: json['name'],
      age: json['age'],
      gender: json['gender'],
      landHolding: json['landHolding'],
      crop: json['crop'],
      caste: json['caste'],
      income: json['income'],
      createdAt: DateTime.parse(json['createdAt']),
    );
  }
}
