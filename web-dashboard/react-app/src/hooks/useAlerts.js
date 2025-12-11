import { useState, useEffect, useCallback } from 'react';

const useAlerts = (apiClient, options = {}) => {
  const {
    pollInterval = 5000,
    unacknowledgedOnly = false,
    limit = 10,
    autoStart = true
  } = options;

  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchAlerts = useCallback(async () => {
    try {
      setError(null);
      const params = new URLSearchParams();
      if (unacknowledgedOnly) params.append('unacknowledged_only', 'true');
      params.append('limit', limit.toString());

      const response = await apiClient.get(`/api/alerts/latest?${params.toString()}`);
      setAlerts(response.data || []);
    } catch (err) {
      console.error('Error fetching alerts:', err);
      setError(err.message || 'Failed to fetch alerts');
    } finally {
      setLoading(false);
    }
  }, [apiClient, unacknowledgedOnly, limit]);

  useEffect(() => {
    if (autoStart) {
      fetchAlerts();
      
      const interval = setInterval(() => {
        fetchAlerts();
      }, pollInterval);

      return () => clearInterval(interval);
    }
  }, [fetchAlerts, pollInterval, autoStart]);

  const acknowledgeAlert = useCallback(async (alertId) => {
    try {
      await apiClient.post(`/api/alerts/${alertId}/acknowledge`);
      // Refresh alerts after acknowledgment
      await fetchAlerts();
      return true;
    } catch (err) {
      console.error('Error acknowledging alert:', err);
      throw err;
    }
  }, [apiClient, fetchAlerts]);

  return {
    alerts,
    loading,
    error,
    refetch: fetchAlerts,
    acknowledgeAlert
  };
};

export default useAlerts;









