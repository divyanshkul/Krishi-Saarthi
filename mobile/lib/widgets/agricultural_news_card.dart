import 'package:flutter/material.dart';

class AgriculturalNewsCard extends StatelessWidget {
  const AgriculturalNewsCard({super.key});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        boxShadow: [BoxShadow(color: Colors.black12, blurRadius: 6)],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: const [
          Text(
            'Agriculture News',
            style: TextStyle(fontWeight: FontWeight.bold),
          ),
          SizedBox(height: 8),
          ListTile(
            title: Text('5% increase in MSP for Rabi crops'),
            subtitle: Text('Ministry of Agriculture · 2 hours ago'),
          ),
          ListTile(
            title: Text('Warning of seasonal rain in Madhya Pradesh'),
            subtitle: Text('Meteorological Department · 4 hours ago'),
          ),
        ],
      ),
    );
  }
}
