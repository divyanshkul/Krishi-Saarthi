import 'package:flutter/material.dart';
import '../models/particle.dart';

class ParticleAnimationWidget extends StatefulWidget {
  final double radius;
  final int particleCount;

  const ParticleAnimationWidget({
    super.key,
    this.radius = 150.0,
    this.particleCount = 120,
  });

  @override
  State<ParticleAnimationWidget> createState() => _ParticleAnimationWidgetState();
}

class _ParticleAnimationWidgetState extends State<ParticleAnimationWidget>
    with SingleTickerProviderStateMixin {
  late AnimationController _animationController;
  late List<Particle> particles;
  double centerX = 0;
  double centerY = 0;

  @override
  void initState() {
    super.initState();
    
    _animationController = AnimationController(
      duration: const Duration(milliseconds: 16), // ~60 FPS
      vsync: this,
    )..repeat();

    particles = [];
    _initializeParticles();

    _animationController.addListener(() {
      setState(() {
        _updateParticles();
      });
    });
  }

  void _initializeParticles() {
    particles.clear();
    // Only initialize if we have valid center coordinates
    if (centerX > 0 && centerY > 0) {
      for (int i = 0; i < widget.particleCount; i++) {
        particles.add(Particle.createRandom(
          centerX: centerX,
          centerY: centerY,
          radius: widget.radius,
        ));
      }
    }
  }

  void _updateParticles() {
    for (final particle in particles) {
      particle.update(
        centerX: centerX,
        centerY: centerY,
        radius: widget.radius,
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        final newCenterX = constraints.maxWidth / 2;
        final newCenterY = constraints.maxHeight / 2;
        
        // Initialize or reinitialize particles if center changed
        if (particles.isEmpty || (centerX != newCenterX || centerY != newCenterY)) {
          centerX = newCenterX;
          centerY = newCenterY;
          _initializeParticles();
        }

        return CustomPaint(
          painter: ParticlePainter(particles: particles),
          size: Size(constraints.maxWidth, constraints.maxHeight),
        );
      },
    );
  }

  @override
  void dispose() {
    _animationController.dispose();
    super.dispose();
  }
}

class ParticlePainter extends CustomPainter {
  final List<Particle> particles;

  ParticlePainter({required this.particles});

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..style = PaintingStyle.fill
      ..strokeCap = StrokeCap.round;

    for (final particle in particles) {
      paint.color = particle.color.withValues(alpha: particle.opacity);
      
      canvas.drawCircle(
        Offset(particle.x, particle.y),
        particle.size / 2,
        paint,
      );
    }
  }

  @override
  bool shouldRepaint(CustomPainter oldDelegate) => true;
}