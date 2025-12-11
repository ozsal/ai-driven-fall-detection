import React, { useState, useEffect } from 'react';
import './AlertBanner.css';

const AlertBanner = ({ alerts, onDismiss }) => {
  const [visibleAlerts, setVisibleAlerts] = useState([]);

  useEffect(() => {
    // Show only unacknowledged alerts, sorted by severity
    const unacknowledged = alerts
      .filter(alert => !alert.acknowledged)
      .sort((a, b) => {
        const severityOrder = { extreme: 4, high: 3, medium: 2, low: 1 };
        return severityOrder[b.severity] - severityOrder[a.severity];
      })
      .slice(0, 3); // Show max 3 alerts in banner
    
    setVisibleAlerts(unacknowledged);
  }, [alerts]);

  if (visibleAlerts.length === 0) {
    return null;
  }

  const getSeverityClass = (severity) => {
    return `alert-banner alert-banner-${severity}`;
  };

  const getSeverityIcon = (severity, alertType) => {
    if (alertType === 'fire_risk') {
      return '🔥';
    }
    if (alertType === 'unsafe_temperature') {
      return '🌡️';
    }
    if (alertType === 'unsafe_humidity') {
      return '💧';
    }
    if (alertType === 'rapid_fluctuation') {
      return '⚠️';
    }
    return '🚨';
  };

  return (
    <div className="alert-banner-container">
      {visibleAlerts.map(alert => (
        <div
          key={alert.id}
          className={getSeverityClass(alert.severity)}
        >
          <div className="alert-banner-content">
            <span className="alert-banner-icon">
              {getSeverityIcon(alert.severity, alert.alert_type)}
            </span>
            <span className="alert-banner-message">{alert.message}</span>
            <span className="alert-banner-device">{alert.device_id}</span>
          </div>
          <button
            className="alert-banner-dismiss"
            onClick={() => onDismiss && onDismiss(alert.id)}
            aria-label="Dismiss alert"
          >
            ×
          </button>
        </div>
      ))}
    </div>
  );
};

export default AlertBanner;









