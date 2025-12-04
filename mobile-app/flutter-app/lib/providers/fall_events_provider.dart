import 'package:flutter/foundation.dart';
import '../services/api_service.dart';

class FallEventsProvider with ChangeNotifier {
  List<Map<String, dynamic>> _events = [];
  bool _isLoading = false;
  String? _error;

  List<Map<String, dynamic>> get events => _events;
  bool get isLoading => _isLoading;
  String? get error => _error;

  Future<void> fetchEvents() async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      _events = await ApiService.getFallEvents();
      _error = null;
    } catch (e) {
      _error = e.toString();
      _events = [];
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> acknowledgeEvent(String eventId) async {
    try {
      await ApiService.acknowledgeEvent(eventId);
      await fetchEvents(); // Refresh list
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
  }
}



