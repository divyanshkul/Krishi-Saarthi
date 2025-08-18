class Crop {
  final String? id;
  final String cropType;
  final String variety;
  final DateTime sowingDate;
  final String district;
  final String state;
  final DateTime createdAt;

  Crop({
    this.id,
    required this.cropType,
    required this.variety,
    required this.sowingDate,
    required this.district,
    required this.state,
    DateTime? createdAt,
  }) : createdAt = createdAt ?? DateTime.now();

  Map<String, dynamic> toJson() {
    return {
      'crop_type': cropType,
      'variety': variety,
      'sowing_date': sowingDate.toIso8601String(),
      'district': district,
      'state': state,
      'createdAt': createdAt.toIso8601String(),
    };
  }

  factory Crop.fromJson(Map<String, dynamic> json, String id) {
    return Crop(
      id: id,
      cropType: json['crop_type'],
      variety: json['variety'],
      sowingDate: DateTime.parse(json['sowing_date']),
      district: json['district'],
      state: json['state'],
      createdAt: DateTime.parse(json['createdAt']),
    );
  }

  int get daysSinceSowing {
    return DateTime.now().difference(sowingDate).inDays;
  }

  String get currentStage {
    final days = daysSinceSowing;

    // Generic farming stages based on days since sowing
    if (days <= 10) {
      return 'Seed Germination';
    } else if (days <= 30) {
      return 'Vegetative Growth';
    } else if (days <= 60) {
      return 'Flowering/Pollination';
    } else if (days <= 90) {
      return 'Fruit Development';
    } else if (days <= 120) {
      return 'Maturation';
    } else {
      return 'Harvest Ready';
    }
  }
}
