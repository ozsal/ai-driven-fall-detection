import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';

class SettingsScreen extends StatefulWidget {
  const SettingsScreen({super.key});

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  bool emailAlerts = true;
  bool pushNotifications = true;
  double alertThreshold = 5.0;
  String apiUrl = 'http://localhost:8000';

  @override
  void initState() {
    super.initState();
    loadSettings();
  }

  Future<void> loadSettings() async {
    final prefs = await SharedPreferences.getInstance();
    setState(() {
      emailAlerts = prefs.getBool('emailAlerts') ?? true;
      pushNotifications = prefs.getBool('pushNotifications') ?? true;
      alertThreshold = prefs.getDouble('alertThreshold') ?? 5.0;
      apiUrl = prefs.getString('apiUrl') ?? 'http://localhost:8000';
    });
  }

  Future<void> saveSettings() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool('emailAlerts', emailAlerts);
    await prefs.setBool('pushNotifications', pushNotifications);
    await prefs.setDouble('alertThreshold', alertThreshold);
    await prefs.setString('apiUrl', apiUrl);

    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Settings saved')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Settings'),
        actions: [
          TextButton(
            onPressed: saveSettings,
            child: const Text(
              'Save',
              style: TextStyle(color: Colors.white),
            ),
          ),
        ],
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          const Text(
            'Notification Preferences',
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 16),
          SwitchListTile(
            title: const Text('Email Alerts'),
            subtitle: const Text('Receive fall alerts via email'),
            value: emailAlerts,
            onChanged: (value) {
              setState(() {
                emailAlerts = value;
              });
            },
          ),
          SwitchListTile(
            title: const Text('Push Notifications'),
            subtitle: const Text('Receive push notifications for falls'),
            value: pushNotifications,
            onChanged: (value) {
              setState(() {
                pushNotifications = value;
              });
            },
          ),
          const SizedBox(height: 24),
          const Text(
            'Alert Threshold',
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 8),
          Text('Minimum severity score to trigger alerts: ${alertThreshold.toStringAsFixed(1)}/10'),
          Slider(
            value: alertThreshold,
            min: 0,
            max: 10,
            divisions: 20,
            label: alertThreshold.toStringAsFixed(1),
            onChanged: (value) {
              setState(() {
                alertThreshold = value;
              });
            },
          ),
          const SizedBox(height: 24),
          const Text(
            'API Configuration',
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 8),
          TextField(
            decoration: const InputDecoration(
              labelText: 'API URL',
              border: OutlineInputBorder(),
            ),
            value: apiUrl,
            onChanged: (value) {
              setState(() {
                apiUrl = value;
              });
            },
          ),
        ],
      ),
    );
  }
}

