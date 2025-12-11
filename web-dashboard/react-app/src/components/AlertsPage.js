import React, { useState, useEffect, useCallback } from 'react';
import AlertCard from './AlertCard';
import './AlertsPage.css';

const AlertsPage = ({ apiClient }) => {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({
    device_id: '',
    alert_type: '',
    severity: '',
    acknowledged: null
  });
  const [stats, setStats] = useState(null);

  const fetchAlerts = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const params = new URLSearchParams();
      if (filters.device_id) params.append('device_id', filters.device_id);
      if (filters.alert_type) params.append('alert_type', filters.alert_type);
      if (filters.severity) params.append('severity', filters.severity);
      if (filters.acknowledged !== null) params.append('acknowledged', filters.acknowledged);

      const response = await apiClient.get(`/api/alerts?${params.toString()}`);
      setAlerts(response.data || []);
    } catch (err) {
      console.error('Error fetching alerts:', err);
      setError('Failed to fetch alerts. Please try again.');
    } finally {
      setLoading(false);
    }
  }, [apiClient, filters]);

  const fetchStats = useCallback(async () => {
    try {
      const response = await apiClient.get('/api/alerts/stats/summary');
      setStats(response.data);
    } catch (err) {
      console.error('Error fetching alert stats:', err);
    }
  }, [apiClient]);

  useEffect(() => {
    fetchAlerts();
    fetchStats();
    
    // Refresh every 5 seconds
    const interval = setInterval(() => {
      fetchAlerts();
      fetchStats();
    }, 5000);

    return () => clearInterval(interval);
  }, [fetchAlerts, fetchStats]);

  const handleAcknowledge = async (alertId) => {
    try {
      await apiClient.post(`/api/alerts/${alertId}/acknowledge`);
      // Refresh alerts after acknowledgment
      fetchAlerts();
      fetchStats();
    } catch (err) {
      console.error('Error acknowledging alert:', err);
      alert('Failed to acknowledge alert. Please try again.');
    }
  };

  const handleViewDetails = (alert) => {
    // Show alert details in a modal or navigate to details page
    console.log('View details for alert:', alert);
    // You can implement a modal here
    alert(`Alert Details:\n\n${JSON.stringify(alert, null, 2)}`);
  };

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({
      ...prev,
      [key]: value
    }));
  };

  const clearFilters = () => {
    setFilters({
      device_id: '',
      alert_type: '',
      severity: '',
      acknowledged: null
    });
  };

  if (loading && alerts.length === 0) {
    return (
      <div className="alerts-page">
        <div className="alerts-loading">Loading alerts...</div>
      </div>
    );
  }

  return (
    <div className="alerts-page">
      <div className="alerts-header">
        <h1>Alerts</h1>
        {stats && (
          <div className="alerts-stats">
            <div className="stat-item">
              <span className="stat-label">Total</span>
              <span className="stat-value">{stats.total}</span>
            </div>
            <div className="stat-item stat-unacknowledged">
              <span className="stat-label">Unacknowledged</span>
              <span className="stat-value">{stats.unacknowledged}</span>
            </div>
            <div className="stat-item stat-extreme">
              <span className="stat-label">Extreme</span>
              <span className="stat-value">{stats.by_severity?.extreme || 0}</span>
            </div>
          </div>
        )}
      </div>

      <div className="alerts-filters">
        <div className="filter-group">
          <label>Device ID</label>
          <input
            type="text"
            value={filters.device_id}
            onChange={(e) => handleFilterChange('device_id', e.target.value)}
            placeholder="Filter by device..."
          />
        </div>
        <div className="filter-group">
          <label>Alert Type</label>
          <select
            value={filters.alert_type}
            onChange={(e) => handleFilterChange('alert_type', e.target.value)}
          >
            <option value="">All Types</option>
            <option value="fire_risk">Fire Risk</option>
            <option value="unsafe_temperature">Unsafe Temperature</option>
            <option value="unsafe_humidity">Unsafe Humidity</option>
            <option value="rapid_fluctuation">Rapid Fluctuation</option>
            <option value="motion_anomaly">Motion Anomaly</option>
            <option value="sensor_failure">Sensor Failure</option>
          </select>
        </div>
        <div className="filter-group">
          <label>Severity</label>
          <select
            value={filters.severity}
            onChange={(e) => handleFilterChange('severity', e.target.value)}
          >
            <option value="">All Severities</option>
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
            <option value="extreme">Extreme</option>
          </select>
        </div>
        <div className="filter-group">
          <label>Status</label>
          <select
            value={filters.acknowledged === null ? '' : filters.acknowledged ? 'true' : 'false'}
            onChange={(e) => handleFilterChange('acknowledged', e.target.value === '' ? null : e.target.value === 'true')}
          >
            <option value="">All</option>
            <option value="false">Unacknowledged</option>
            <option value="true">Acknowledged</option>
          </select>
        </div>
        <button className="filter-clear" onClick={clearFilters}>
          Clear Filters
        </button>
      </div>

      {error && (
        <div className="alerts-error">
          {error}
        </div>
      )}

      <div className="alerts-list">
        {alerts.length === 0 ? (
          <div className="alerts-empty">
            <p>No alerts found</p>
            <p className="alerts-empty-subtitle">Alerts will appear here when sensor data triggers threshold conditions</p>
          </div>
        ) : (
          alerts.map(alert => (
            <AlertCard
              key={alert.id}
              alert={alert}
              onAcknowledge={handleAcknowledge}
              onViewDetails={handleViewDetails}
            />
          ))
        )}
      </div>
    </div>
  );
};

export default AlertsPage;




