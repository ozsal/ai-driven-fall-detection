import React from 'react';
import './AlertCard.css';

const AlertCard = ({ alert, onAcknowledge, onViewDetails }) => {
  const getSeverityClass = (severity) => {
    return `alert-card alert-card-${severity}`;
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

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleString();
  };

  const getSensorValuesDisplay = (sensorValues) => {
    if (!sensorValues || Object.keys(sensorValues).length === 0) {
      return null;
    }

    const items = [];
    if (sensorValues.temperature_c !== undefined) {
      items.push(`Temp: ${sensorValues.temperature_c.toFixed(1)}°C`);
    }
    if (sensorValues.humidity_percent !== undefined) {
      items.push(`Humidity: ${sensorValues.humidity_percent.toFixed(1)}%`);
    }
    if (sensorValues.distance_cm !== undefined) {
      items.push(`Distance: ${sensorValues.distance_cm.toFixed(1)}cm`);
    }
    if (sensorValues.motion_detected !== undefined) {
      items.push(`Motion: ${sensorValues.motion_detected ? 'Yes' : 'No'}`);
    }

    return items.length > 0 ? items.join(' • ') : null;
  };

  return (
    <div className={getSeverityClass(alert.severity)}>
      <div className="alert-card-header">
        <div className="alert-card-icon">
          {getSeverityIcon(alert.severity, alert.alert_type)}
        </div>
        <div className="alert-card-title">
          <h3>{alert.message}</h3>
          <span className="alert-card-type">{alert.alert_type.replace('_', ' ').toUpperCase()}</span>
        </div>
        <div className="alert-card-severity-badge">
          {alert.severity.toUpperCase()}
        </div>
      </div>

      <div className="alert-card-body">
        <div className="alert-card-info">
          <div className="alert-card-info-item">
            <span className="label">Device:</span>
            <span className="value">{alert.device_id}</span>
          </div>
          <div className="alert-card-info-item">
            <span className="label">Triggered:</span>
            <span className="value">{formatDate(alert.triggered_at)}</span>
          </div>
          {getSensorValuesDisplay(alert.sensor_values) && (
            <div className="alert-card-info-item">
              <span className="label">Values:</span>
              <span className="value">{getSensorValuesDisplay(alert.sensor_values)}</span>
            </div>
          )}
        </div>

        {alert.acknowledged && (
          <div className="alert-card-acknowledged">
            ✓ Acknowledged {alert.acknowledged_at && `at ${formatDate(alert.acknowledged_at)}`}
            {alert.acknowledged_by && ` by ${alert.acknowledged_by}`}
          </div>
        )}
      </div>

      <div className="alert-card-actions">
        {!alert.acknowledged && (
          <button
            className="alert-card-btn alert-card-btn-acknowledge"
            onClick={() => onAcknowledge && onAcknowledge(alert.id)}
          >
            Acknowledge
          </button>
        )}
        <button
          className="alert-card-btn alert-card-btn-details"
          onClick={() => onViewDetails && onViewDetails(alert)}
        >
          View Details
        </button>
      </div>
    </div>
  );
};

export default AlertCard;









