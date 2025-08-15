import 'package:flutter/material.dart';
import '../widgets/app_header.dart';

class MandiPage extends StatelessWidget {
  const MandiPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Column(
        children: [
          const AppHeader(),
          const SizedBox(height: 12),
          Expanded(
            child: ListView(
              padding: const EdgeInsets.all(12),
              children: [
                _priceCard(
                  'Wheat',
                  '₹2,450/quintal',
                  'Bhopal Mandi',
                  -1.2,
                  'AI Suggestion: Wait for the next 7 days - 78% probability of price increase.',
                ),
                const SizedBox(height: 12),
                _priceCard(
                  'Soybean',
                  '₹4,850/quintal',
                  'Indore Mandi (45 km)',
                  0.6,
                  'AI Suggestion: Sell immediately - possible decline in the next 5 days (82% confidence)',
                ),
                const SizedBox(height: 12),
                _build7DayChartPlaceholder(),
                const SizedBox(height: 12),
                _buildGovtSchemesCard(),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _priceCard(
    String title,
    String price,
    String mandi,
    double change,
    String suggestion,
  ) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        boxShadow: [BoxShadow(color: Colors.black12, blurRadius: 6)],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                title,
                style: const TextStyle(
                  fontWeight: FontWeight.bold,
                  fontSize: 18,
                ),
              ),
              Text(
                '$change%',
                style: TextStyle(color: change < 0 ? Colors.red : Colors.green),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Text(
            price,
            style: const TextStyle(
              fontSize: 28,
              fontWeight: FontWeight.bold,
              color: Colors.green,
            ),
          ),
          const SizedBox(height: 4),
          Text(mandi, style: const TextStyle(color: Colors.grey)),
          const SizedBox(height: 8),
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: Colors.green.shade50,
              borderRadius: BorderRadius.circular(8),
            ),
            child: Text(suggestion),
          ),
        ],
      ),
    );
  }

  Widget _build7DayChartPlaceholder() {
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
            '7-Day Price Forecast (LSTM Model)',
            style: TextStyle(fontWeight: FontWeight.bold),
          ),
          SizedBox(height: 8),
          SizedBox(height: 80, child: Center(child: Text('Chart placeholder'))),
        ],
      ),
    );
  }

  Widget _buildGovtSchemesCard() {
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
              'You are eligible · Next installment: 15th December',
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
