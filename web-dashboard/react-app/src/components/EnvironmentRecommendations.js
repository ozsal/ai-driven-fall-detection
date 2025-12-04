import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Alert,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Grid,
  LinearProgress
} from '@mui/material';
import {
  ExpandMore,
  Thermostat,
  WaterDrop,
  Air,
  DirectionsWalk,
  Warning,
  CheckCircle,
  AcUnit,
  Dehumidify
} from '@mui/icons-material';
import axios from 'axios';
import { API_BASE_URL } from '../config';

const EnvironmentRecommendations = ({ deviceId = null }) => {
  const [recommendations, setRecommendations] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchRecommendations();
    // Refresh every 5 minutes
    const interval = setInterval(fetchRecommendations, 300000);
    return () => clearInterval(interval);
  }, [deviceId]);

  const fetchRecommendations = async () => {
    try {
      setLoading(true);
      setError(null);
      const params = new URLSearchParams();
      if (deviceId) params.append('device_id', deviceId);
      params.append('hours', '24');
      
      const response = await axios.get(
        `${API_BASE_URL}/api/environment/recommendations?${params.toString()}`
      );
      setRecommendations(response.data);
    } catch (err) {
      console.error('Error fetching recommendations:', err);
      setError('Failed to load environment recommendations');
    } finally {
      setLoading(false);
    }
  };

  const getIcon = (iconName) => {
    const icons = {
      thermostat: <Thermostat />,
      ac_unit: <AcUnit />,
      water_drop: <WaterDrop />,
      dehumidify: <Dehumidify />,
      air: <Air />,
      directions_walk: <DirectionsWalk />,
      warning: <Warning />,
      check_circle: <CheckCircle />
    };
    return icons[iconName] || <Warning />;
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'high':
        return 'error';
      case 'medium':
        return 'warning';
      case 'low':
        return 'info';
      default:
        return 'default';
    }
  };

  const getScoreColor = (score) => {
    if (score >= 80) return 'success';
    if (score >= 60) return 'warning';
    return 'error';
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ mb: 2 }}>
        {error}
      </Alert>
    );
  }

  if (!recommendations || recommendations.status === 'insufficient_data') {
    return (
      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>
          Environment Recommendations
        </Typography>
        <Alert severity="info">
          Insufficient sensor data available. Please ensure sensors are active and sending data.
        </Alert>
      </Paper>
    );
  }

  const { environment_score, analysis, recommendations: recs } = recommendations;

  return (
    <Box>
      <Typography variant="h6" gutterBottom sx={{ mb: 2 }}>
        Environment Recommendations
      </Typography>

      {/* Environment Score Card */}
      <Card sx={{ mb: 3, bgcolor: 'background.paper' }}>
        <CardContent>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} sm={6}>
              <Typography color="textSecondary" gutterBottom>
                Overall Environment Score
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <Typography variant="h3" color={`${getScoreColor(environment_score)}.main`}>
                  {environment_score}
                </Typography>
                <Typography variant="h6" color="textSecondary">
                  / 100
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={12} sm={6}>
              <LinearProgress
                variant="determinate"
                value={environment_score}
                color={getScoreColor(environment_score)}
                sx={{ height: 10, borderRadius: 5 }}
              />
              <Typography variant="caption" color="textSecondary" sx={{ mt: 1, display: 'block' }}>
                {environment_score >= 80
                  ? 'Optimal conditions'
                  : environment_score >= 60
                  ? 'Good conditions'
                  : 'Needs improvement'}
              </Typography>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Current Conditions Summary */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Typography variant="subtitle1" gutterBottom>
          Current Conditions
        </Typography>
        <Grid container spacing={2}>
          {analysis.temperature?.current && (
            <Grid item xs={6} sm={3}>
              <Box>
                <Typography variant="caption" color="textSecondary">
                  Temperature
                </Typography>
                <Typography variant="h6">
                  {analysis.temperature.current}°C
                </Typography>
                <Chip
                  label={analysis.temperature.status.replace('_', ' ')}
                  size="small"
                  color={analysis.temperature.status === 'optimal' ? 'success' : 'warning'}
                />
              </Box>
            </Grid>
          )}
          {analysis.humidity?.current && (
            <Grid item xs={6} sm={3}>
              <Box>
                <Typography variant="caption" color="textSecondary">
                  Humidity
                </Typography>
                <Typography variant="h6">
                  {analysis.humidity.current}%
                </Typography>
                <Chip
                  label={analysis.humidity.status.replace('_', ' ')}
                  size="small"
                  color={analysis.humidity.status === 'optimal' ? 'success' : 'warning'}
                />
              </Box>
            </Grid>
          )}
          {analysis.motion?.activity_level && (
            <Grid item xs={6} sm={3}>
              <Box>
                <Typography variant="caption" color="textSecondary">
                  Activity Level
                </Typography>
                <Typography variant="h6" textTransform="capitalize">
                  {analysis.motion.activity_level}
                </Typography>
                <Chip
                  label={`${Math.round(analysis.motion.activity_ratio * 100)}% motion`}
                  size="small"
                />
              </Box>
            </Grid>
          )}
          {analysis.fall_risk?.risk_level && (
            <Grid item xs={6} sm={3}>
              <Box>
                <Typography variant="caption" color="textSecondary">
                  Fall Risk
                </Typography>
                <Typography variant="h6" textTransform="capitalize">
                  {analysis.fall_risk.risk_level}
                </Typography>
                <Chip
                  label={`Score: ${analysis.fall_risk.risk_score}`}
                  size="small"
                  color={getPriorityColor(analysis.fall_risk.risk_level)}
                />
              </Box>
            </Grid>
          )}
        </Grid>
      </Paper>

      {/* Recommendations List */}
      {recs && recs.length > 0 ? (
        <Box>
          <Typography variant="subtitle1" gutterBottom sx={{ mb: 2 }}>
            Recommendations ({recs.length})
          </Typography>
          {recs.map((rec) => (
            <Accordion key={rec.id} sx={{ mb: 1 }}>
              <AccordionSummary expandIcon={<ExpandMore />}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, width: '100%' }}>
                  <Box sx={{ color: `${getPriorityColor(rec.priority)}.main` }}>
                    {getIcon(rec.icon)}
                  </Box>
                  <Box sx={{ flexGrow: 1 }}>
                    <Typography variant="subtitle1">{rec.title}</Typography>
                    <Typography variant="caption" color="textSecondary">
                      {rec.category.replace('_', ' ').toUpperCase()}
                    </Typography>
                  </Box>
                  <Chip
                    label={rec.priority}
                    size="small"
                    color={getPriorityColor(rec.priority)}
                  />
                </Box>
              </AccordionSummary>
              <AccordionDetails>
                <Box>
                  <Typography variant="body2" paragraph>
                    {rec.description}
                  </Typography>
                  <Box sx={{ bgcolor: 'action.hover', p: 2, borderRadius: 1, mb: 2 }}>
                    <Typography variant="subtitle2" gutterBottom>
                      Recommended Action:
                    </Typography>
                    <Typography variant="body2">{rec.action}</Typography>
                  </Box>
                  <Box sx={{ bgcolor: 'success.light', p: 2, borderRadius: 1 }}>
                    <Typography variant="subtitle2" gutterBottom>
                      Expected Impact:
                    </Typography>
                    <Typography variant="body2">{rec.impact}</Typography>
                  </Box>
                </Box>
              </AccordionDetails>
            </Accordion>
          ))}
        </Box>
      ) : (
        <Alert severity="success">
          No recommendations at this time. Environment conditions are optimal!
        </Alert>
      )}

      {/* Data Info */}
      <Typography variant="caption" color="textSecondary" sx={{ mt: 2, display: 'block' }}>
        Analysis based on {recommendations.data_points_analyzed} sensor readings from the last 24 hours
      </Typography>
    </Box>
  );
};

export default EnvironmentRecommendations;

