import React, { useState, useEffect } from 'react';
import AlertBanner from './AlertBanner';
import useAlerts from '../hooks/useAlerts';
import './DashboardWithAlerts.css';

/**
 * Example Dashboard component with integrated alerts
 * Replace your existing Dashboard component with this or integrate AlertBanner into it
 */
const DashboardWithAlerts = ({ apiClient, websocket }) => {
  const [alerts, setAlerts] = useState([]);
  const { alerts: latestAlerts, acknowledgeAlert } = useAlerts(apiClient, {
    pollInterval: 5000,
    unacknowledgedOnly: true,
    limit: 10
  });

  // Update alerts when latestAlerts changes
  useEffect(() => {
    setAlerts(latestAlerts);
  }, [latestAlerts]);

  // Listen for real-time alert updates via WebSocket
  useEffect(() => {
    if (!websocket) return;

    const handleMessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === 'alert') {
          // Add new alert to the list
          setAlerts(prev => {
            // Check if alert already exists
            const exists = prev.find(a => a.id === data.alert.id);
            if (exists) return prev;
            
            // Add new alert at the beginning
            return [data.alert, ...prev].slice(0, 10);
          });
        }
      } catch (err) {
        console.error('Error parsing WebSocket message:', err);
      }
    };

    websocket.addEventListener('message', handleMessage);
    return () => {
      websocket.removeEventListener('message', handleMessage);
    };
  }, [websocket]);

  const handleDismissAlert = async (alertId) => {
    try {
      await acknowledgeAlert(alertId);
      // Alert will be removed from list after acknowledgment
    } catch (err) {
      console.error('Error dismissing alert:', err);
    }
  };

  return (
    <div className="dashboard-with-alerts">
      {/* Alert Banner at the top */}
      <AlertBanner 
        alerts={alerts} 
        onDismiss={handleDismissAlert}
      />

      {/* Your existing dashboard content */}
      <div className="dashboard-content" style={{ marginTop: alerts.length > 0 ? '80px' : '0' }}>
        {/* Add your existing dashboard components here */}
        <h1>Dashboard</h1>
        {/* SensorData, Statistics, etc. */}
      </div>
    </div>
  );
};

export default DashboardWithAlerts;

