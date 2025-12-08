/**
 * Alert Service
 * Handles API calls for alerts
 */

class AlertService {
  constructor(apiClient) {
    this.apiClient = apiClient;
  }

  /**
   * Get all alerts with optional filters
   */
  async getAlerts(filters = {}) {
    const params = new URLSearchParams();
    
    if (filters.device_id) params.append('device_id', filters.device_id);
    if (filters.alert_type) params.append('alert_type', filters.alert_type);
    if (filters.severity) params.append('severity', filters.severity);
    if (filters.acknowledged !== undefined) params.append('acknowledged', filters.acknowledged);
    if (filters.limit) params.append('limit', filters.limit);
    if (filters.offset) params.append('offset', filters.offset);

    const response = await this.apiClient.get(`/api/alerts?${params.toString()}`);
    return response.data;
  }

  /**
   * Get latest alerts for real-time dashboard
   */
  async getLatestAlerts(limit = 10, unacknowledgedOnly = false) {
    const params = new URLSearchParams();
    params.append('limit', limit.toString());
    if (unacknowledgedOnly) params.append('unacknowledged_only', 'true');

    const response = await this.apiClient.get(`/api/alerts/latest?${params.toString()}`);
    return response.data;
  }

  /**
   * Get a specific alert by ID
   */
  async getAlert(alertId) {
    const response = await this.apiClient.get(`/api/alerts/${alertId}`);
    return response.data;
  }

  /**
   * Acknowledge an alert
   */
  async acknowledgeAlert(alertId) {
    const response = await this.apiClient.post(`/api/alerts/${alertId}/acknowledge`);
    return response.data;
  }

  /**
   * Get alert statistics
   */
  async getAlertStats() {
    const response = await this.apiClient.get('/api/alerts/stats/summary');
    return response.data;
  }

  /**
   * Create a new alert (admin only)
   */
  async createAlert(alertData) {
    const response = await this.apiClient.post('/api/alerts', alertData);
    return response.data;
  }
}

export default AlertService;

