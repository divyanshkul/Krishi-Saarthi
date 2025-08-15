import 'dart:math';
import 'dart:ui';

class Particle {
  double x;
  double y;
  double vx;
  double vy;
  double size;
  double opacity;
  Color color;
  double maxOpacity;
  
  Particle({
    required this.x,
    required this.y,
    required this.vx,
    required this.vy,
    required this.size,
    required this.opacity,
    required this.color,
    required this.maxOpacity,
  });

  static Particle createRandom({
    required double centerX,
    required double centerY,
    required double radius,
  }) {
    final random = Random();
    
    // Generate random angle and distance from center
    final angle = random.nextDouble() * 2 * pi;
    final distance = random.nextDouble() * radius;
    
    // Position within circular boundary
    final x = centerX + cos(angle) * distance;
    final y = centerY + sin(angle) * distance;
    
    // Random velocity for floating motion (faster and more dynamic)
    final vx = (random.nextDouble() - 0.5) * 1.5;
    final vy = (random.nextDouble() - 0.5) * 1.5;
    
    // Random size and opacity (more variety)
    final size = 1.5 + random.nextDouble() * 5;
    final maxOpacity = 0.4 + random.nextDouble() * 0.6;
    final opacity = maxOpacity;
    
    // Darker green color variations
    final greenShades = [
      const Color(0xFF6B8E23), // Olive drab
      const Color(0xFF228B22), // Forest green
      const Color(0xFF32CD32), // Lime green
      const Color(0xFF7CFC00), // Lawn green
      const Color(0xFF9ACD32), // Yellow green
      const Color(0xFF8FBC8F), // Dark sea green
    ];
    
    final color = greenShades[random.nextInt(greenShades.length)];
    
    return Particle(
      x: x,
      y: y,
      vx: vx,
      vy: vy,
      size: size,
      opacity: opacity,
      color: color,
      maxOpacity: maxOpacity,
    );
  }
  
  void update({
    required double centerX,
    required double centerY,
    required double radius,
  }) {
    // Update position
    x += vx;
    y += vy;
    
    // Keep particles within circular boundary
    final dx = x - centerX;
    final dy = y - centerY;
    final distance = sqrt(dx * dx + dy * dy);
    
    if (distance > radius) {
      // Bounce back towards center
      final angle = atan2(dy, dx);
      x = centerX + cos(angle) * radius;
      y = centerY + sin(angle) * radius;
      
      // Reverse velocity component pointing away from center
      vx = -vx * 0.8;
      vy = -vy * 0.8;
    }
    
    // Add slight random movement (more dynamic)
    final random = Random();
    vx += (random.nextDouble() - 0.5) * 0.05;
    vy += (random.nextDouble() - 0.5) * 0.05;
    
    // Limit velocity (allow faster movement)
    vx = vx.clamp(-2.0, 2.0);
    vy = vy.clamp(-2.0, 2.0);
    
    // Subtle opacity fluctuation
    final opacityChange = (random.nextDouble() - 0.5) * 0.02;
    opacity = (opacity + opacityChange).clamp(0.2, maxOpacity);
  }
}