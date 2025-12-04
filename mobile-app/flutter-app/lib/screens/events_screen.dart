import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:intl/intl.dart';
import '../providers/fall_events_provider.dart';

class EventsScreen extends StatefulWidget {
  const EventsScreen({super.key});

  @override
  State<EventsScreen> createState() => _EventsScreenState();
}

class _EventsScreenState extends State<EventsScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      Provider.of<FallEventsProvider>(context, listen: false).fetchEvents();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Fall Events'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () {
              Provider.of<FallEventsProvider>(context, listen: false).fetchEvents();
            },
          ),
        ],
      ),
      body: Consumer<FallEventsProvider>(
        builder: (context, provider, child) {
          if (provider.isLoading) {
            return const Center(child: CircularProgressIndicator());
          }

          if (provider.events.isEmpty) {
            return const Center(
              child: Text('No events found'),
            );
          }

          return ListView.builder(
            itemCount: provider.events.length,
            itemBuilder: (context, index) {
              final event = provider.events[index];
              return _EventListItem(event: event);
            },
          );
        },
      ),
    );
  }
}

class _EventListItem extends StatelessWidget {
  final Map<String, dynamic> event;

  const _EventListItem({required this.event});

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
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      child: ExpansionTile(
        leading: CircleAvatar(
          backgroundColor: _getSeverityColor(severity),
          child: Text(
            severity.toStringAsFixed(1),
            style: const TextStyle(
              color: Colors.white,
              fontWeight: FontWeight.bold,
            ),
          ),
        ),
        title: Text(
          '${_getSeverityLabel(severity)} Severity Fall',
          style: const TextStyle(fontWeight: FontWeight.bold),
        ),
        subtitle: Text(
          DateFormat('MMM dd, yyyy HH:mm:ss').format(timestamp),
        ),
        children: [
          Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _DetailRow('Location', event['location'] ?? 'Unknown'),
                _DetailRow('Severity Score', '${severity.toStringAsFixed(2)}/10'),
                _DetailRow('Verified', event['verified'] == true ? 'Yes' : 'No'),
                _DetailRow('User ID', event['user_id'] ?? 'Unknown'),
                if (event['acknowledged'] == true)
                  const Chip(
                    label: Text('Acknowledged'),
                    backgroundColor: Colors.green,
                  ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _DetailRow extends StatelessWidget {
  final String label;
  final String value;

  const _DetailRow(this.label, this.value);

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 100,
            child: Text(
              '$label:',
              style: const TextStyle(fontWeight: FontWeight.bold),
            ),
          ),
          Expanded(
            child: Text(value),
          ),
        ],
      ),
    );
  }
}



