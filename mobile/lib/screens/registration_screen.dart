import 'package:flutter/material.dart';
import '../models/user_profile.dart';
import '../services/firebase_service.dart';
import 'home_screen.dart';

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

  // Page 1 Controllers
  final TextEditingController _nameController = TextEditingController();
  final TextEditingController _ageController = TextEditingController();
  String? _gender;
  String? _landHolding;

  // Page 2 Controllers
  String? _crop;
  String? _caste;
  String? _income;

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
              Navigator.of(context).pop();
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
            'Farming & Socio-Economic Info',
            style: TextStyle(
              fontSize: 24,
              fontWeight: FontWeight.bold,
              color: Color(0xFF2D4F2B),
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'Help us understand you better.',
            style: TextStyle(fontSize: 16, color: Color(0xFF708A58)),
          ),
          const SizedBox(height: 30),
          _buildDropdown(
            ['Rice', 'Wheat', 'Maize', 'Sugarcane', 'Cotton'],
            'Which crops do you usually grow?',
            (value) => _crop = value,
          ),
          const SizedBox(height: 20),
          _buildDropdown(
            ['General', 'OBC', 'SC', 'ST'],
            'Caste Category',
            (value) => _caste = value,
          ),
          const SizedBox(height: 20),
          _buildDropdown(
            ['< ₹1,00,000', '₹1,00,000 - ₹5,00,000', '> ₹5,00,000'],
            'Annual Family Income',
            (value) => _income = value,
          ),
          const SizedBox(height: 40),
          _buildSubmitButton(),
        ],
      ),
    );
  }

  Widget _buildTextField(
    TextEditingController controller,
    String label, {
    TextInputType keyboardType = TextInputType.text,
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
      validator: (value) {
        if (value == null || value.isEmpty) {
          return 'Please enter $label';
        }
        return null;
      },
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
        if (value == null) {
          return 'Please select an option';
        }
        return null;
      },
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
    if (_formKey.currentState!.validate()) {
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
          crop: _crop!,
          caste: _caste!,
          income: _income!,
        );

        String? userId = await FirebaseService.saveUserProfile(userProfile);

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
