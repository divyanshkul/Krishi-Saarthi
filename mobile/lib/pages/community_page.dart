import 'package:flutter/material.dart';
import '../widgets/app_header.dart';

class CommunityPage extends StatelessWidget {
  const CommunityPage({super.key});

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
                _buildShareStoryButton(),
                const SizedBox(height: 12),
                _buildPostCard(
                  'Ram Singh',
                  '2 hours ago - Sehore',
                  'Wheat yield increased by 30% this year with organic manure!',
                ),
                const SizedBox(height: 12),
                _buildPostCard(
                  'Sunita Devi',
                  '5 hours ago - Vidisha',
                  'There was a problem of leaf curl in tomatoes. AI immediately identified it from the photo and suggested medicine. The crop was saved!',
                ),
                const SizedBox(height: 12),
                _buildNewsCard(),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildShareStoryButton() {
    return ElevatedButton.icon(
      onPressed: () {},
      icon: const Icon(Icons.add),
      label: const Text('Share your story'),
      style: ElevatedButton.styleFrom(backgroundColor: Colors.orange),
    );
  }

  Widget _buildPostCard(String name, String meta, String text) {
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
            children: [
              CircleAvatar(child: Text(name[0])),
              const SizedBox(width: 8),
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    name,
                    style: const TextStyle(fontWeight: FontWeight.bold),
                  ),
                  Text(
                    meta,
                    style: const TextStyle(fontSize: 12, color: Colors.grey),
                  ),
                ],
              ),
            ],
          ),
          const SizedBox(height: 8),
          Text(text),
          const SizedBox(height: 8),
          Row(
            children: const [
              Icon(Icons.thumb_up),
              SizedBox(width: 8),
              Icon(Icons.comment),
              SizedBox(width: 8),
              Icon(Icons.share),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildNewsCard() {
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
