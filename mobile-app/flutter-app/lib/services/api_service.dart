import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

class ApiService {
  static String get baseUrl {
    // In production, get from settings
    return 'http://localhost:8000';
  }

  static Future<Map<String, dynamic>> getStatistics() async {
    final response = await http.get(
      Uri.parse('$baseUrl/api/statistics'),
    );

    if (response.statusCode == 200) {
      return json.decode(response.body);
    } else {
      throw Exception('Failed to load statistics');
    }
  }

  static Future<List<Map<String, dynamic>>> getFallEvents({int limit = 100}) async {
    final response = await http.get(
      Uri.parse('$baseUrl/api/fall-events?limit=$limit'),
    );

    if (response.statusCode == 200) {
      final List<dynamic> data = json.decode(response.body);
      return data.cast<Map<String, dynamic>>();
    } else {
      throw Exception('Failed to load fall events');
    }
  }

  static Future<Map<String, dynamic>> getFallEvent(String eventId) async {
    final response = await http.get(
      Uri.parse('$baseUrl/api/fall-events/$eventId'),
    );

    if (response.statusCode == 200) {
      return json.decode(response.body);
    } else {
      throw Exception('Failed to load fall event');
    }
  }

  static Future<void> acknowledgeEvent(String eventId) async {
    final response = await http.post(
      Uri.parse('$baseUrl/api/fall-events/$eventId/acknowledge'),
    );

    if (response.statusCode != 200) {
      throw Exception('Failed to acknowledge event');
    }
  }

  static Future<List<Map<String, dynamic>>> getDevices() async {
    final response = await http.get(
      Uri.parse('$baseUrl/api/devices'),
    );

    if (response.statusCode == 200) {
      final List<dynamic> data = json.decode(response.body);
      return data.cast<Map<String, dynamic>>();
    } else {
      throw Exception('Failed to load devices');
    }
  }
}

