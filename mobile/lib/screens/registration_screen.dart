import 'package:flutter/material.dart';
import '../models/user_profile.dart';
import '../models/crop.dart';
import '../services/firebase_service.dart';
import 'home_screen.dart';
import 'splash_screen.dart';

class RegistrationScreen extends StatefulWidget {
  const RegistrationScreen({super.key});

  @override
  State<RegistrationScreen> createState() => _RegistrationScreenState();
}

class _RegistrationScreenState extends State<RegistrationScreen> {
  final PageController _pageController = PageController();
  int _currentPage = 0;
  bool _isLoading = false;

  final _formKey = GlobalKey<FormState>();

  // Page 1 Controllers (Basic Info)
  final TextEditingController _nameController = TextEditingController();
  final TextEditingController _ageController = TextEditingController();
  String? _gender;
  String? _landHolding;

  // Page 2 Controllers (Location & Farming Info)
  String? _state;
  String? _district;
  String? _crop;
  final TextEditingController _varietyController = TextEditingController();
  String? _caste;
  String? _income;
  DateTime? _sowingDate;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFFFF1CA),
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: Color(0xFF2D4F2B)),
          onPressed: () {
            if (_currentPage == 0) {
              Navigator.pushReplacement(
                context,
                MaterialPageRoute(builder: (context) => const SplashScreen()),
              );
            } else {
              _pageController.previousPage(
                duration: const Duration(milliseconds: 300),
                curve: Curves.easeInOut,
              );
            }
          },
        ),
      ),
      body: Form(
        key: _formKey,
        child: Column(
          children: [
            Padding(
              padding: const EdgeInsets.symmetric(
                horizontal: 20.0,
                vertical: 10.0,
              ),
              child: RegistrationProgressBar(currentPage: _currentPage),
            ),
            Expanded(
              child: PageView(
                controller: _pageController,
                onPageChanged: (int page) {
                  setState(() {
                    _currentPage = page;
                  });
                },
                children: [_buildPage1(), _buildPage2()],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildPage1() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(20.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Basic Information',
            style: TextStyle(
              fontSize: 28,
              fontWeight: FontWeight.bold,
              color: Color(0xFF2D4F2B),
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'Let\'s start with the basics.',
            style: TextStyle(fontSize: 16, color: Color(0xFF708A58)),
          ),
          const SizedBox(height: 30),
          _buildTextField(_nameController, 'Full Name'),
          const SizedBox(height: 20),
          _buildTextField(
            _ageController,
            'Age',
            keyboardType: TextInputType.number,
          ),
          const SizedBox(height: 20),
          _buildDropdown(
            ['Male', 'Female', 'Other'],
            'Gender',
            (value) => _gender = value,
          ),
          const SizedBox(height: 20),
          _buildDropdown(
            ['Less than 2 ha', '2–5 ha', 'More than 5 ha'],
            'Total Land Holding',
            (value) => _landHolding = value,
          ),
          const SizedBox(height: 40),
          _buildNextButton(),
        ],
      ),
    );
  }

  Widget _buildPage2() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(20.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Location & Farming Info',
            style: TextStyle(
              fontSize: 24,
              fontWeight: FontWeight.bold,
              color: Color(0xFF2D4F2B),
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'Help us provide personalized recommendations.',
            style: TextStyle(fontSize: 16, color: Color(0xFF708A58)),
          ),
          const SizedBox(height: 30),
          _buildDropdown(
            [
              'Madhya Pradesh',
              'Uttar Pradesh',
              'Punjab',
              'Haryana',
              'Gujarat',
              'Maharashtra',
              'Karnataka',
              'Tamil Nadu',
              'Andhra Pradesh',
              'Rajasthan',
            ],
            'State',
            (value) {
              setState(() {
                _state = value;
                _district = null; // Reset district when state changes
              });
            },
          ),
          const SizedBox(height: 20),
          _buildDropdown(_getDistrictsForState(_state), 'District', (value) {
            setState(() {
              _district = value;
            });
          }),
          const SizedBox(height: 20),
          _buildDropdown(
            [
              'Rice',
              'Wheat',
              'Maize',
              'Sugarcane',
              'Cotton',
              'Soybean',
              'Pulses',
              'Vegetables',
              'Fruits',
            ],
            'Primary Crop',
            (value) => _crop = value,
          ),
          const SizedBox(height: 20),
          _buildTextField(
            _varietyController,
            'Crop Variety (e.g., HD-2967 for Wheat)',
            required: false,
          ),
          const SizedBox(height: 20),
          _buildDatePicker('Sowing Date', (date) => _sowingDate = date),
          const SizedBox(height: 20),
          _buildDropdown(
            ['General', 'OBC', 'SC', 'ST'],
            'Category',
            (value) => _caste = value,
          ),
          const SizedBox(height: 20),
          _buildDropdown(
            [
              'Less than ₹50,000',
              '₹50,000 - ₹1,00,000',
              '₹1,00,000 - ₹2,00,000',
              'More than ₹2,00,000',
            ],
            'Annual Income',
            (value) => _income = value,
          ),
          const SizedBox(height: 40),
          _buildSubmitButton(),
        ],
      ),
    );
  }

  List<String> _getDistrictsForState(String? state) {
    if (state == null) return ['Select state first'];

    switch (state) {
      case 'Madhya Pradesh':
        return [
          'Bhopal',
          'Indore',
          'Gwalior',
          'Jabalpur',
          'Ujjain',
          'Sagar',
          'Dewas',
          'Satna',
          'Ratlam',
          'Mandsaur',
        ];
      case 'Uttar Pradesh':
        return [
          'Lucknow',
          'Kanpur',
          'Agra',
          'Varanasi',
          'Meerut',
          'Allahabad',
          'Bareilly',
          'Gorakhpur',
          'Mathura',
          'Firozabad',
        ];
      case 'Punjab':
        return [
          'Chandigarh',
          'Ludhiana',
          'Amritsar',
          'Jalandhar',
          'Patiala',
          'Bathinda',
          'Mohali',
          'Hoshiarpur',
        ];
      case 'Haryana':
        return [
          'Gurugram',
          'Faridabad',
          'Panipat',
          'Ambala',
          'Yamunanagar',
          'Rohtak',
          'Hisar',
          'Karnal',
        ];
      case 'Gujarat':
        return [
          'Ahmedabad',
          'Surat',
          'Vadodara',
          'Rajkot',
          'Bhavnagar',
          'Jamnagar',
          'Junagadh',
          'Gandhinagar',
        ];
      case 'Maharashtra':
        return [
          'Mumbai',
          'Pune',
          'Nagpur',
          'Nashik',
          'Aurangabad',
          'Solapur',
          'Kolhapur',
          'Sangli',
        ];
      case 'Karnataka':
        return [
          'Bangalore',
          'Mysore',
          'Hubli',
          'Mangalore',
          'Belgaum',
          'Gulbarga',
          'Shimoga',
          'Tumkur',
        ];
      case 'Tamil Nadu':
        return [
          'Chennai',
          'Coimbatore',
          'Madurai',
          'Tiruchirappalli',
          'Salem',
          'Tirunelveli',
          'Erode',
          'Vellore',
        ];
      case 'Andhra Pradesh':
        return [
          'Visakhapatnam',
          'Vijayawada',
          'Guntur',
          'Nellore',
          'Kurnool',
          'Rajahmundry',
          'Tirupati',
          'Anantapur',
        ];
      case 'Rajasthan':
        return [
          'Jaipur',
          'Jodhpur',
          'Udaipur',
          'Kota',
          'Bikaner',
          'Ajmer',
          'Alwar',
          'Bhilwara',
        ];
      default:
        return ['Select state first'];
    }
  }

  Widget _buildTextField(
    TextEditingController controller,
    String label, {
    TextInputType keyboardType = TextInputType.text,
    bool required = true,
  }) {
    return TextFormField(
      controller: controller,
      keyboardType: keyboardType,
      decoration: InputDecoration(
        labelText: label,
        labelStyle: TextStyle(color: Color(0xFF708A58)),
        filled: true,
        fillColor: Colors.white,
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(10),
          borderSide: BorderSide.none,
        ),
      ),
      validator: required
          ? (value) {
              if (value == null || value.isEmpty) {
                return 'Please enter $label';
              }
              return null;
            }
          : null,
    );
  }

  Widget _buildDropdown(
    List<String> items,
    String hint,
    Function(String?) onChanged,
  ) {
    return DropdownButtonFormField<String>(
      decoration: InputDecoration(
        labelText: hint,
        labelStyle: TextStyle(color: Color(0xFF708A58)),
        filled: true,
        fillColor: Colors.white,
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(10),
          borderSide: BorderSide.none,
        ),
      ),
      items: items.map((String value) {
        return DropdownMenuItem<String>(value: value, child: Text(value));
      }).toList(),
      onChanged: onChanged,
      validator: (value) {
        if (value == null ||
            value == 'Select state first' ||
            value == 'Select district') {
          return 'Please select an option';
        }
        return null;
      },
    );
  }

  Widget _buildDatePicker(String label, Function(DateTime) onSelected) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: TextStyle(
            fontWeight: FontWeight.w500,
            color: Color(0xFF708A58),
          ),
        ),
        const SizedBox(height: 8),
        InkWell(
          onTap: () async {
            final DateTime? picked = await showDatePicker(
              context: context,
              initialDate: DateTime.now().subtract(Duration(days: 30)),
              firstDate: DateTime.now().subtract(Duration(days: 365)),
              lastDate: DateTime.now(),
              builder: (context, child) {
                return Theme(
                  data: Theme.of(context).copyWith(
                    colorScheme: ColorScheme.light(
                      primary: Color(0xFF2D4F2B),
                      onPrimary: Colors.white,
                      surface: Colors.white,
                      onSurface: Colors.black,
                    ),
                  ),
                  child: child!,
                );
              },
            );
            if (picked != null) {
              onSelected(picked);
              setState(() {});
            }
          },
          child: Container(
            padding: EdgeInsets.symmetric(horizontal: 12, vertical: 16),
            decoration: BoxDecoration(
              color: Colors.white,
              border: Border.all(color: Colors.grey.shade300),
              borderRadius: BorderRadius.circular(10),
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  _sowingDate != null
                      ? '${_sowingDate!.day}/${_sowingDate!.month}/${_sowingDate!.year}'
                      : 'Select sowing date',
                  style: TextStyle(
                    color: _sowingDate != null
                        ? Colors.black
                        : Colors.grey.shade600,
                  ),
                ),
                Icon(Icons.calendar_today, color: Color(0xFF708A58)),
              ],
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildNextButton() {
    return SizedBox(
      width: double.infinity,
      child: ElevatedButton(
        style: ElevatedButton.styleFrom(
          backgroundColor: const Color(0xFF2D4F2B),
          padding: const EdgeInsets.symmetric(vertical: 15),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(10),
          ),
        ),
        onPressed: () {
          if (_formKey.currentState!.validate()) {
            _formKey.currentState!.save();
            _pageController.nextPage(
              duration: const Duration(milliseconds: 300),
              curve: Curves.easeInOut,
            );
          }
        },
        child: const Text(
          'Next',
          style: TextStyle(fontSize: 20, color: Color(0xFFFFB823)),
        ),
      ),
    );
  }

  Widget _buildSubmitButton() {
    return SizedBox(
      width: double.infinity,
      child: ElevatedButton(
        style: ElevatedButton.styleFrom(
          backgroundColor: const Color(0xFF2D4F2B),
          padding: const EdgeInsets.symmetric(vertical: 15),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(10),
          ),
        ),
        onPressed: _isLoading ? null : _handleSubmit,
        child: _isLoading
            ? const CircularProgressIndicator(color: Color(0xFFFFB823))
            : const Text(
                'Submit',
                style: TextStyle(fontSize: 20, color: Color(0xFFFFB823)),
              ),
      ),
    );
  }

  Future<void> _handleSubmit() async {
    if (_formKey.currentState!.validate() && _sowingDate != null) {
      _formKey.currentState!.save();

      setState(() {
        _isLoading = true;
      });

      try {
        UserProfile userProfile = UserProfile(
          name: _nameController.text,
          age: int.parse(_ageController.text),
          gender: _gender!,
          landHolding: _landHolding!,
          district: _district!,
          state: _state!,
          caste: _caste!,
          income: _income!,
        );

        Crop crop = Crop(
          cropType: _crop!,
          variety: _varietyController.text.isNotEmpty
              ? _varietyController.text
              : 'Standard',
          sowingDate: _sowingDate!,
          district: _district!,
          state: _state!,
        );

        String? userId = await FirebaseService.saveUserProfile(
          userProfile,
          crop,
        );

        if (mounted) {
          if (userId != null) {
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(
                content: Text('Profile saved successfully!'),
                backgroundColor: Colors.green,
              ),
            );
            Navigator.pushAndRemoveUntil(
              context,
              MaterialPageRoute(builder: (context) => const HomeScreen()),
              (Route<dynamic> route) => false,
            );
          } else {
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(
                content: Text('Failed to save profile. Please try again.'),
                backgroundColor: Colors.red,
              ),
            );
          }
        }
      } catch (e) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text('Error: ${e.toString()}'),
              backgroundColor: Colors.red,
            ),
          );
        }
      } finally {
        if (mounted) {
          setState(() {
            _isLoading = false;
          });
        }
      }
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text(
            'Please fill all required fields including sowing date',
          ),
          backgroundColor: Colors.orange,
        ),
      );
    }
  }
}

class RegistrationProgressBar extends StatelessWidget {
  final int currentPage;

  const RegistrationProgressBar({super.key, required this.currentPage});

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Expanded(child: _buildStep(0, 'Basic Info')),
        Container(
          width: 50,
          height: 2,
          color: currentPage == 1
              ? const Color(0xFF2D4F2B)
              : Colors.grey.shade300,
        ),
        Expanded(child: _buildStep(1, 'Farming Info')),
      ],
    );
  }

  Widget _buildStep(int index, String title) {
    final bool isActive = currentPage >= index;
    return Column(
      children: [
        CircleAvatar(
          radius: 15,
          backgroundColor: isActive
              ? const Color(0xFF2D4F2B)
              : Colors.grey.shade300,
          child: Icon(Icons.check, color: Colors.white, size: 18),
        ),
        const SizedBox(height: 5),
        Text(
          title,
          style: TextStyle(
            color: isActive ? const Color(0xFF2D4F2B) : Colors.grey.shade500,
            fontWeight: isActive ? FontWeight.bold : FontWeight.normal,
          ),
        ),
      ],
    );
  }
}
