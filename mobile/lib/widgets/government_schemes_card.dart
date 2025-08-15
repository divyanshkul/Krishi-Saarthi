import 'package:flutter/material.dart';

class GovernmentSchemesCard extends StatelessWidget {
  const GovernmentSchemesCard({super.key});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.orange.shade50,
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Government Schemes',
            style: TextStyle(fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 8),
          ListTile(
            leading: const Icon(Icons.account_balance_wallet),
            title: const Text('PM-KISAN'),
            subtitle: const Text(
              'You are eligible · Next installment: 15th August',
            ),
          ),
          const Divider(),
          ListTile(
            leading: const Icon(Icons.shield),
            title: const Text('Crop Insurance Scheme'),
            subtitle: const Text('Application deadline: 30th November'),
          ),
        ],
      ),
    );
  }
}
