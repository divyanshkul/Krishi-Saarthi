import 'package:flutter/material.dart';
import 'package:lottie/lottie.dart';
import 'registration_screen.dart';

class SplashScreen extends StatefulWidget {
  const SplashScreen({super.key});

  @override
  State<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<Offset> _tractorOffsetAnimation;
  late Animation<double> _titleFadeAnimation;
  late Animation<Offset> _titleSlideAnimation;
  late Animation<double> _taglineFadeAnimation;
  late Animation<double> _buttonFadeAnimation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: const Duration(seconds: 6),
      vsync: this,
    )..forward();

    _titleFadeAnimation = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(
        parent: _controller,
        curve: const Interval(0.0, 0.25, curve: Curves.easeIn),
      ),
    );

    _titleSlideAnimation =
        Tween<Offset>(begin: const Offset(0, 0.5), end: Offset.zero).animate(
          CurvedAnimation(
            parent: _controller,
            curve: const Interval(0.0, 0.25, curve: Curves.easeIn),
          ),
        );

    _taglineFadeAnimation = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(
        parent: _controller,
        curve: const Interval(0.25, 0.5, curve: Curves.easeIn),
      ),
    );

    _tractorOffsetAnimation = Tween<Offset>(
      begin: const Offset(-1.5, 0.0),
      end: const Offset(1.5, 0.0),
    ).animate(CurvedAnimation(parent: _controller, curve: Curves.linear));

    _buttonFadeAnimation = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(
        parent: _controller,
        curve: const Interval(0.5, 0.75, curve: Curves.easeOut),
      ),
    );
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFFFF1CA),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: <Widget>[
            SlideTransition(
              position: _titleSlideAnimation,
              child: FadeTransition(
                opacity: _titleFadeAnimation,
                child: const Text(
                  'Krishi Saarthi',
                  style: TextStyle(
                    fontSize: 48,
                    fontWeight: FontWeight.bold,
                    color: Color(0xFF2D4F2B),
                  ),
                ),
              ),
            ),
            FadeTransition(
              opacity: _taglineFadeAnimation,
              child: const Text(
                'Desh ke Kisaan ka Digital Saathi',
                style: TextStyle(fontSize: 20, color: Color(0xFF708A58)),
              ),
            ),
            const SizedBox(height: 50),
            SlideTransition(
              position: _tractorOffsetAnimation,
              child: Lottie.asset(
                'assets/lottie/tractor_verde.json',
                width: 200,
                height: 200,
                fit: BoxFit.contain,
              ),
            ),
            const SizedBox(height: 100),
            FadeTransition(
              opacity: _buttonFadeAnimation,
              child: ElevatedButton(
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF2D4F2B),
                  padding: const EdgeInsets.symmetric(
                    horizontal: 50,
                    vertical: 15,
                  ),
                ),
                onPressed: () {
                  Navigator.pushReplacement(
                    context,
                    MaterialPageRoute(
                      builder: (context) => const RegistrationScreen(),
                    ),
                  );
                },
                child: const Text(
                  'Register Now',
                  style: TextStyle(fontSize: 20, color: Color(0xFFFFB823)),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
