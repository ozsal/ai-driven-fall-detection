import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:intl/intl.dart';
import '../providers/fall_events_provider.dart';
import '../services/api_service.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  Map<String, dynamic>? statistics;
  bool isLoading = true;

  @override
  void initState() {
    super.initState();
    fetchStatistics();
  }

  Future<void> fetchStatistics() async {
    try {
      final stats = await ApiService.getStatistics();
      setState(() {
        statistics = stats;
        isLoading = false;
      });
    } catch (e) {
      setState(() {
        isLoading = false;
      });
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error loading statistics: $e')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Fall Detection Dashboard'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: fetchStatistics,
          ),
        ],
      ),
      body: isLoading
          ? const Center(child: CircularProgressIndicator())
          : RefreshIndicator(
              onRefresh: fetchStatistics,
              child: SingleChildScrollView(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Statistics Cards
                    GridView.count(
                      crossAxisCount: 2,
                      shrinkWrap: true,
                      physics: const NeverScrollableScrollPhysics(),
                      crossAxisSpacing: 16,
                      mainAxisSpacing: 16,
                      children: [
                        _StatCard(
                          title: 'Total Events',
                          value: statistics?['total_fall_events']?.toString() ?? '0',
                          icon: Icons.warning,
                          color: Colors.red,
                        ),
                        _StatCard(
                          title: 'Events (7d)',
                          value: statistics?['recent_events_7d']?.toString() ?? '0',
                          icon: Icons.trending_up,
                          color: Colors.orange,
                        ),
                        _StatCard(
                          title: 'Active Devices',
                          value: statistics?['active_devices']?.toString() ?? '0',
                          icon: Icons.devices,
                          color: Colors.green,
                        ),
                        _StatCard(
                          title: 'Sensor Readings',
                          value: _formatNumber(statistics?['total_sensor_readings'] ?? 0),
                          icon: Icons.sensors,
                          color: Colors.blue,
                        ),
                      ],
                    ),
                    const SizedBox(height: 24),
                    // Recent Events
                    const Text(
                      'Recent Fall Events',
                      style: TextStyle(
                        fontSize: 20,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 16),
                    Consumer<FallEventsProvider>(
                      builder: (context, provider, child) {
                        if (provider.events.isEmpty) {
                          return const Center(
                            child: Padding(
                              padding: EdgeInsets.all(32.0),
                              child: Text('No recent events'),
                            ),
                          );
                        }
                        return ListView.builder(
                          shrinkWrap: true,
                          physics: const NeverScrollableScrollPhysics(),
                          itemCount: provider.events.length > 5 ? 5 : provider.events.length,
                          itemBuilder: (context, index) {
                            final event = provider.events[index];
                            return _EventCard(event: event);
                          },
                        );
                      },
                    ),
                  ],
                ),
              ),
            ),
    );
  }

  String _formatNumber(int number) {
    if (number >= 1000000) {
      return '${(number / 1000000).toStringAsFixed(1)}M';
    } else if (number >= 1000) {
      return '${(number / 1000).toStringAsFixed(1)}K';
    }
    return number.toString();
  }
}

class _StatCard extends StatelessWidget {
  final String title;
  final String value;
  final IconData icon;
  final Color color;

  const _StatCard({
    required this.title,
    required this.value,
    required this.icon,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 4,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(icon, size: 40, color: color),
            const SizedBox(height: 8),
            Text(
              value,
              style: TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.bold,
                color: color,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              title,
              style: const TextStyle(
                fontSize: 12,
                color: Colors.grey,
              ),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }
}

class _EventCard extends StatelessWidget {
  final Map<String, dynamic> event;

  const _EventCard({required this.event});

  Color _getSeverityColor(double score) {
    if (score >= 7) return Colors.red;
    if (score >= 4) return Colors.orange;
    return Colors.green;
  }

  String _getSeverityLabel(double score) {
    if (score >= 7) return 'High';
    if (score >= 4) return 'Medium';
    return 'Low';
  }

  @override
  Widget build(BuildContext context) {
    final severity = event['severity_score']?.toDouble() ?? 0.0;
    final timestamp = event['timestamp'] != null
        ? DateTime.parse(event['timestamp'])
        : DateTime.now();

    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: _getSeverityColor(severity),
          child: const Icon(Icons.warning, color: Colors.white),
        ),
        title: Text(
          'Severity: ${_getSeverityLabel(severity)} (${severity.toStringAsFixed(1)}/10)',
          style: const TextStyle(fontWeight: FontWeight.bold),
        ),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Location: ${event['location'] ?? 'Unknown'}'),
            Text(
              DateFormat('MMM dd, yyyy HH:mm').format(timestamp),
              style: const TextStyle(fontSize: 12, color: Colors.grey),
            ),
          ],
        ),
        trailing: event['verified'] == true
            ? const Icon(Icons.verified, color: Colors.green)
            : const Icon(Icons.help_outline, color: Colors.orange),
        onTap: () {
          // Navigate to event details
        },
      ),
    );
  }
}

