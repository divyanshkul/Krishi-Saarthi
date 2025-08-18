import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../models/user_profile.dart';
import '../models/crop.dart';
import '../services/firebase_service.dart';
import '../providers/language_provider.dart';
import '../widgets/profile_info_card.dart';
import '../widgets/crop_info_card.dart';

class FarmerProfileScreen extends StatefulWidget {
  const FarmerProfileScreen({super.key});

  @override
  State<FarmerProfileScreen> createState() => _FarmerProfileScreenState();
}

class _FarmerProfileScreenState extends State<FarmerProfileScreen> {
  UserProfile? _userProfile;
  List<Crop> _crops = [];
  bool _isLoading = true;
  String? _error;
  bool _isAddingCrop = false;
  bool _isSavingCrop = false;

  // Form controllers for new crop
  final _cropTypeController = TextEditingController();
  final _varietyController = TextEditingController();
  DateTime? _newCropSowingDate;

  @override
  void initState() {
    super.initState();
    _loadUserData();
  }

  Future<void> _loadUserData() async {
    try {
      setState(() {
        _isLoading = true;
        _error = null;
      });

      // Migrate old profile if needed
      await FirebaseService.migrateOldUserProfile();

      // Load user profile and crops
      final userProfile = await FirebaseService.getUserProfile();
      final crops = await FirebaseService.getUserCrops();

      setState(() {
        _userProfile = userProfile;
        _crops = crops;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _error = e.toString();
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final languageProvider = Provider.of<LanguageProvider>(context);

    return Scaffold(
      backgroundColor: const Color(0xFFE8F5E8),
      appBar: AppBar(
        backgroundColor: const Color(0xFF4CAF50),
        foregroundColor: Colors.white,
        elevation: 0,
        title: Text(
          languageProvider.translate('farmerProfile'),
          style: const TextStyle(
            fontSize: 20,
            fontWeight: FontWeight.bold,
            color: Colors.white,
          ),
        ),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: Colors.white),
          onPressed: () => Navigator.of(context).pop(),
        ),
      ),
      body: _isLoading
          ? const Center(
              child: CircularProgressIndicator(color: Color(0xFF2D4F2B)),
            )
          : _error != null
          ? _buildErrorView()
          : _userProfile == null
          ? _buildNoProfileView()
          : _buildProfileView(),
    );
  }

  Widget _buildErrorView() {
    final languageProvider = Provider.of<LanguageProvider>(context);

    return Center(
      child: Padding(
        padding: const EdgeInsets.all(20.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.error_outline, size: 64, color: Colors.red.shade400),
            const SizedBox(height: 16),
            Text(
              languageProvider.translate('errorLoadingProfile'),
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
                color: Colors.red.shade700,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              _error!,
              textAlign: TextAlign.center,
              style: TextStyle(fontSize: 14, color: Colors.red.shade600),
            ),
            const SizedBox(height: 20),
            ElevatedButton(
              onPressed: _loadUserData,
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF2D4F2B),
                foregroundColor: const Color(0xFFFFB823),
              ),
              child: Text(languageProvider.translate('retry')),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildNoProfileView() {
    final languageProvider = Provider.of<LanguageProvider>(context);

    return Center(
      child: Padding(
        padding: const EdgeInsets.all(20.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.person_outline, size: 64, color: Colors.grey.shade400),
            const SizedBox(height: 16),
            Text(
              languageProvider.translate('noProfileFound'),
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
                color: Colors.grey.shade700,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              languageProvider.translate('pleaseCompleteRegistration'),
              textAlign: TextAlign.center,
              style: TextStyle(fontSize: 14, color: Colors.grey.shade600),
            ),
            const SizedBox(height: 20),
            ElevatedButton(
              onPressed: () => Navigator.of(context).pop(),
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF2D4F2B),
                foregroundColor: const Color(0xFFFFB823),
              ),
              child: Text(languageProvider.translate('goBack')),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildProfileView() {
    final languageProvider = Provider.of<LanguageProvider>(context);

    return RefreshIndicator(
      onRefresh: _loadUserData,
      color: const Color(0xFF2D4F2B),
      child: SingleChildScrollView(
        physics: const AlwaysScrollableScrollPhysics(),
        padding: const EdgeInsets.all(20.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Profile Header
            _buildProfileHeader(),
            const SizedBox(height: 20),

            // Basic Information
            _buildSectionTitle(languageProvider.translate('basicInformation')),
            const SizedBox(height: 12),
            ProfileInfoCard(
              icon: Icons.person,
              title: languageProvider.translate('name'),
              value: _userProfile!.name,
            ),
            const SizedBox(height: 8),
            Row(
              children: [
                Expanded(
                  child: ProfileInfoCard(
                    icon: Icons.cake,
                    title: languageProvider.translate('age'),
                    value: '${_userProfile!.age} years',
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: ProfileInfoCard(
                    icon: Icons.wc,
                    title: languageProvider.translate('gender'),
                    value: _userProfile!.gender,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 20),

            // Location Information
            _buildSectionTitle(languageProvider.translate('location')),
            const SizedBox(height: 12),
            ProfileInfoCard(
              icon: Icons.location_on,
              title: languageProvider.translate('location'),
              value: '${_userProfile!.district}, ${_userProfile!.state}',
            ),
            const SizedBox(height: 20),

            // Farm Information
            _buildSectionTitle(languageProvider.translate('farmDetails')),
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(
                  child: ProfileInfoCard(
                    icon: Icons.landscape,
                    title: languageProvider.translate('landHolding'),
                    value: _userProfile!.landHolding,
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: ProfileInfoCard(
                    icon: Icons.category,
                    title: languageProvider.translate('category'),
                    value: _userProfile!.caste,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            ProfileInfoCard(
              icon: Icons.currency_rupee,
              title: languageProvider.translate('annualIncome'),
              value: _userProfile!.income,
            ),
            const SizedBox(height: 20),

            // Crops Information
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                _buildSectionTitle(
                  '${languageProvider.translate('crops')} (${_crops.length})',
                ),
                if (_crops.length < 2 && !_isAddingCrop)
                  Container(
                    decoration: BoxDecoration(
                      color: const Color(0xFF2D4F2B),
                      borderRadius: BorderRadius.circular(20),
                    ),
                    child: IconButton(
                      icon: const Icon(
                        Icons.add,
                        color: Colors.white,
                        size: 20,
                      ),
                      onPressed: () {
                        setState(() {
                          _isAddingCrop = true;
                        });
                      },
                      constraints: const BoxConstraints(
                        minWidth: 36,
                        minHeight: 36,
                      ),
                    ),
                  ),
              ],
            ),
            const SizedBox(height: 12),
            if (_crops.isEmpty && !_isAddingCrop)
              _buildNoCropsView()
            else
              ..._crops.map(
                (crop) => Padding(
                  padding: const EdgeInsets.only(bottom: 12),
                  child: CropInfoCard(
                    crop: crop,
                    showDeleteButton: _crops.length == 2,
                    onDelete: () => _deleteCrop(crop.id!),
                  ),
                ),
              ),

            // Add new crop form
            if (_isAddingCrop)
              Padding(
                padding: const EdgeInsets.only(bottom: 12),
                child: _buildAddCropCard(),
              ),

            const SizedBox(height: 20),

            // Account Information
            _buildSectionTitle(languageProvider.translate('account')),
            const SizedBox(height: 12),
            ProfileInfoCard(
              icon: Icons.access_time,
              title: languageProvider.translate('memberSince'),
              value: _formatDate(_userProfile!.createdAt),
            ),

            const SizedBox(height: 40),
          ],
        ),
      ),
    );
  }

  Widget _buildProfileHeader() {
    final languageProvider = Provider.of<LanguageProvider>(context);

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [const Color(0xFF2D4F2B), const Color(0xFF708A58)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(15),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.1),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Row(
        children: [
          CircleAvatar(
            radius: 35,
            backgroundColor: const Color(0xFFFFB823),
            child: Text(
              _userProfile!.name.isNotEmpty
                  ? _userProfile!.name[0].toUpperCase()
                  : 'F',
              style: const TextStyle(
                fontSize: 28,
                fontWeight: FontWeight.bold,
                color: Color(0xFF2D4F2B),
              ),
            ),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  _userProfile!.name,
                  style: const TextStyle(
                    fontSize: 24,
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  languageProvider.translate('farmer'),
                  style: TextStyle(
                    fontSize: 16,
                    color: Colors.white.withOpacity(0.8),
                  ),
                ),
                const SizedBox(height: 4),
                Row(
                  children: [
                    Icon(
                      Icons.verified,
                      size: 16,
                      color: const Color(0xFFFFB823),
                    ),
                    const SizedBox(width: 4),
                    Text(
                      languageProvider.translate('verifiedProfile'),
                      style: TextStyle(
                        fontSize: 12,
                        color: const Color(0xFFFFB823),
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSectionTitle(String title) {
    return Text(
      title,
      style: const TextStyle(
        fontSize: 18,
        fontWeight: FontWeight.bold,
        color: Color(0xFF2D4F2B),
      ),
    );
  }

  Widget _buildNoCropsView() {
    final languageProvider = Provider.of<LanguageProvider>(context);

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: const Color(0xFFE8F5E8),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: const Color(0xFF2D4F2B).withOpacity(0.2),
          width: 1,
        ),
      ),
      child: Column(
        children: [
          Icon(Icons.eco_outlined, size: 48, color: Colors.grey.shade400),
          const SizedBox(height: 12),
          Text(
            languageProvider.translate('noCropsRegistered'),
            style: TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.w500,
              color: Colors.grey.shade600,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            languageProvider.translate('addCropsDuringRegistration'),
            style: TextStyle(fontSize: 12, color: Colors.grey.shade500),
          ),
        ],
      ),
    );
  }

  String _formatDate(DateTime date) {
    final months = [
      'Jan',
      'Feb',
      'Mar',
      'Apr',
      'May',
      'Jun',
      'Jul',
      'Aug',
      'Sep',
      'Oct',
      'Nov',
      'Dec',
    ];
    return '${date.day} ${months[date.month - 1]} ${date.year}';
  }

  Widget _buildAddCropCard() {
    final languageProvider = Provider.of<LanguageProvider>(context);

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFFE8F5E8),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: const Color(0xFF2D4F2B), width: 2),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 6,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: const Color(0xFF2D4F2B).withOpacity(0.1),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: const Icon(
                  Icons.add_circle_outline,
                  color: Color(0xFF2D4F2B),
                  size: 20,
                ),
              ),
              const SizedBox(width: 12),
              Text(
                languageProvider.translate('addNewCrop'),
                style: const TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                  color: Color(0xFF2D4F2B),
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),

          // Crop Type Dropdown
          _buildCropDropdown(),
          const SizedBox(height: 12),

          // Variety Input
          _buildTextField(
            _varietyController,
            languageProvider.translate('variety'),
            Icons.eco,
          ),
          const SizedBox(height: 12),

          // Sowing Date Picker
          _buildSowingDatePicker(),
          const SizedBox(height: 16),

          // Action Buttons
          Row(
            mainAxisAlignment: MainAxisAlignment.end,
            children: [
              // Cancel Button
              Container(
                decoration: BoxDecoration(
                  border: Border.all(color: Colors.red, width: 2),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: IconButton(
                  icon: const Icon(Icons.close, color: Colors.red),
                  onPressed: _cancelAddCrop,
                  constraints: const BoxConstraints(
                    minWidth: 40,
                    minHeight: 40,
                  ),
                ),
              ),
              const SizedBox(width: 8),
              // Save Button
              Container(
                decoration: BoxDecoration(
                  color: _isSavingCrop ? Colors.grey : const Color(0xFF2D4F2B),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: IconButton(
                  icon: _isSavingCrop
                      ? const SizedBox(
                          width: 20,
                          height: 20,
                          child: CircularProgressIndicator(
                            color: Colors.white,
                            strokeWidth: 2,
                          ),
                        )
                      : const Icon(Icons.check, color: Colors.white),
                  onPressed: _isSavingCrop ? null : _saveCrop,
                  constraints: const BoxConstraints(
                    minWidth: 40,
                    minHeight: 40,
                  ),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildCropDropdown() {
    final languageProvider = Provider.of<LanguageProvider>(context);
    final cropTypes = [
      'Rice',
      'Wheat',
      'Maize',
      'Sugarcane',
      'Cotton',
      'Soybean',
      'Pulses',
      'Vegetables',
      'Fruits',
      'Other',
    ];

    return DropdownButtonFormField<String>(
      value: _cropTypeController.text.isEmpty ? null : _cropTypeController.text,
      decoration: InputDecoration(
        labelText: languageProvider.translate('cropType'),
        labelStyle: const TextStyle(color: Color(0xFF708A58)),
        filled: true,
        fillColor: const Color(0xFFE8F5E8),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: Color(0xFF2D4F2B)),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: Color(0xFF2D4F2B), width: 2),
        ),
        prefixIcon: const Icon(Icons.agriculture, color: Color(0xFF2D4F2B)),
      ),
      items: cropTypes.map((String value) {
        return DropdownMenuItem<String>(value: value, child: Text(value));
      }).toList(),
      onChanged: (value) {
        setState(() {
          _cropTypeController.text = value ?? '';
        });
      },
    );
  }

  Widget _buildTextField(
    TextEditingController controller,
    String label,
    IconData icon,
  ) {
    return TextFormField(
      controller: controller,
      decoration: InputDecoration(
        labelText: label,
        labelStyle: const TextStyle(color: Color(0xFF708A58)),
        filled: true,
        fillColor: const Color(0xFFE8F5E8),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: Color(0xFF2D4F2B)),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: Color(0xFF2D4F2B), width: 2),
        ),
        prefixIcon: Icon(icon, color: const Color(0xFF2D4F2B)),
      ),
    );
  }

  Widget _buildSowingDatePicker() {
    final languageProvider = Provider.of<LanguageProvider>(context);

    return InkWell(
      onTap: () async {
        final DateTime? picked = await showDatePicker(
          context: context,
          initialDate: _newCropSowingDate ?? DateTime.now(),
          firstDate: DateTime.now().subtract(const Duration(days: 365)),
          lastDate: DateTime.now(),
          builder: (context, child) {
            return Theme(
              data: Theme.of(context).copyWith(
                colorScheme: const ColorScheme.light(
                  primary: Color(0xFF2D4F2B),
                  onPrimary: Colors.white,
                  surface: Colors.white,
                  onSurface: Color(0xFF2D4F2B),
                ),
              ),
              child: child!,
            );
          },
        );
        if (picked != null) {
          setState(() {
            _newCropSowingDate = picked;
          });
        }
      },
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: const Color(0xFFE8F5E8),
          border: Border.all(color: const Color(0xFF2D4F2B)),
          borderRadius: BorderRadius.circular(12),
        ),
        child: Row(
          children: [
            const Icon(Icons.calendar_today, color: Color(0xFF2D4F2B)),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    languageProvider.translate('sowingDate'),
                    style: const TextStyle(
                      fontSize: 12,
                      color: Color(0xFF708A58),
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                  const SizedBox(height: 2),
                  Text(
                    _newCropSowingDate != null
                        ? _formatDate(_newCropSowingDate!)
                        : languageProvider.translate('selectDate'),
                    style: TextStyle(
                      fontSize: 16,
                      color: _newCropSowingDate != null
                          ? const Color(0xFF2D4F2B)
                          : Colors.grey,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  void _cancelAddCrop() {
    setState(() {
      _isAddingCrop = false;
      _cropTypeController.clear();
      _varietyController.clear();
      _newCropSowingDate = null;
    });
  }

  Future<void> _saveCrop() async {
    if (_cropTypeController.text.isEmpty ||
        _varietyController.text.isEmpty ||
        _newCropSowingDate == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Please fill all fields'),
          backgroundColor: Colors.orange,
        ),
      );
      return;
    }

    setState(() {
      _isSavingCrop = true;
    });

    try {
      final newCrop = Crop(
        cropType: _cropTypeController.text,
        variety: _varietyController.text,
        sowingDate: _newCropSowingDate!,
        district: _userProfile!.district,
        state: _userProfile!.state,
      );

      // Save to Firebase
      await FirebaseService.addCrop(newCrop);

      // Refresh the crops list
      await _loadUserData();

      // Reset form
      _cancelAddCrop();

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Crop added successfully!'),
            backgroundColor: Colors.green,
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error adding crop: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } finally {
      if (mounted) {
        setState(() {
          _isSavingCrop = false;
        });
      }
    }
  }

  Future<void> _deleteCrop(String cropId) async {
    try {
      // Delete from Firebase
      bool success = await FirebaseService.deleteCrop(cropId);

      if (success) {
        // Refresh the crops list
        await _loadUserData();

        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('Crop deleted successfully!'),
              backgroundColor: Colors.green,
            ),
          );
        }
      } else {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('Failed to delete crop'),
              backgroundColor: Colors.red,
            ),
          );
        }
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error deleting crop: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }
}
