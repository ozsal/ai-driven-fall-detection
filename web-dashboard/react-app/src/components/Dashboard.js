import React, { useState, useEffect } from 'react';
import {
  Grid,
  Paper,
  Typography,
  Box,
  Card,
  CardContent,
  Alert,
  CircularProgress
} from '@mui/material';
import {
  Line,
  Bar,
  Doughnut
} from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js';
import { useWebSocket } from '../context/WebSocketContext';
import axios from 'axios';
import { API_BASE_URL } from '../config';
import { format } from 'date-fns';
import EnvironmentRecommendations from './EnvironmentRecommendations';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
);

const Dashboard = () => {
  const [stats, setStats] = useState(null);
  const [recentEvents, setRecentEvents] = useState([]);
  const [sensorData, setSensorData] = useState([]);
  const [loading, setLoading] = useState(true);
  const { messages } = useWebSocket();

  useEffect(() => {
    fetchDashboardData();
    const interval = setInterval(fetchDashboardData, 5000); // Refresh every 5 seconds
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    // Process WebSocket messages
    const latestMessage = messages[messages.length - 1];
    if (latestMessage) {
      if (latestMessage.type === 'fall_event') {
        fetchDashboardData(); // Refresh on fall event
      } else if (latestMessage.type === 'sensor_data') {
        // Update sensor data
        setSensorData((prev) => [latestMessage.data, ...prev].slice(0, 50));
      }
    }
  }, [messages]);

  const fetchDashboardData = async () => {
    try {
      const [statsRes, eventsRes] = await Promise.all([
        axios.get(`${API_BASE_URL}/api/statistics`),
        axios.get(`${API_BASE_URL}/api/fall-events?limit=5`)
      ]);

      setStats(statsRes.data);
      setRecentEvents(eventsRes.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  // Chart data
  const fallEventsChart = {
    labels: recentEvents.map((e, i) => `Event ${i + 1}`),
    datasets: [{
      label: 'Severity Score',
      data: recentEvents.map(e => e.severity_score),
      backgroundColor: recentEvents.map(e =>
        e.severity_score >= 7 ? 'rgba(244, 67, 54, 0.8)' :
        e.severity_score >= 4 ? 'rgba(255, 152, 0, 0.8)' :
        'rgba(76, 175, 80, 0.8)'
      ),
      borderColor: 'rgba(0, 0, 0, 0.1)',
      borderWidth: 1
    }]
  };

  const deviceStatusChart = {
    labels: ['Online', 'Offline'],
    datasets: [{
      data: [
        stats?.active_devices || 0,
        Math.max(0, (stats?.total_devices || 0) - (stats?.active_devices || 0))
      ],
      backgroundColor: ['rgba(76, 175, 80, 0.8)', 'rgba(158, 158, 158, 0.8)']
    }]
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>

      {/* Statistics Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Fall Events
              </Typography>
              <Typography variant="h4">
                {stats?.total_fall_events || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Events (7 Days)
              </Typography>
              <Typography variant="h4">
                {stats?.recent_events_7d || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Active Devices
              </Typography>
              <Typography variant="h4">
                {stats?.active_devices || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Sensor Readings
              </Typography>
              <Typography variant="h4">
                {(stats?.total_sensor_readings || 0).toLocaleString()}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Recent Fall Events Alert */}
      {recentEvents.length > 0 && recentEvents[0].severity_score >= 5 && (
        <Alert severity="warning" sx={{ mb: 3 }}>
          Recent high-severity fall detected! Check Events page for details.
        </Alert>
      )}

      {/* Charts */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Recent Fall Events - Severity Scores
            </Typography>
            <Bar data={fallEventsChart} options={{
              responsive: true,
              scales: {
                y: {
                  beginAtZero: true,
                  max: 10
                }
              }
            }} />
          </Paper>
        </Grid>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Device Status
            </Typography>
            <Doughnut data={deviceStatusChart} options={{ responsive: true }} />
          </Paper>
        </Grid>
      </Grid>

      {/* Environment Recommendations */}
      <Paper sx={{ p: 3, mt: 3 }}>
        <EnvironmentRecommendations />
      </Paper>

      {/* Recent Events List */}
      <Paper sx={{ p: 2, mt: 3 }}>
        <Typography variant="h6" gutterBottom>
          Recent Fall Events
        </Typography>
        {recentEvents.length === 0 ? (
          <Typography color="textSecondary">No recent events</Typography>
        ) : (
          recentEvents.map((event, index) => (
            <Box key={index} sx={{ mb: 2, p: 2, border: '1px solid #e0e0e0', borderRadius: 1 }}>
              <Typography variant="subtitle1">
                {format(new Date(event.timestamp), 'PPpp')}
              </Typography>
              <Typography>
                Severity: {event.severity_score}/10 | 
                Location: {event.location || 'Unknown'} | 
                Verified: {event.verified ? 'Yes' : 'No'}
              </Typography>
            </Box>
          ))
        )}
      </Paper>
    </Box>
  );
};

export default Dashboard;



