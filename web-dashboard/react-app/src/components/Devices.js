import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  Card,
  CardContent,
  Chip,
  CircularProgress
} from '@mui/material';
import axios from 'axios';
import { API_BASE_URL } from '../config';
import { format } from 'date-fns';

const Devices = () => {
  const [devices, setDevices] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDevices();
    const interval = setInterval(fetchDevices, 5000);
    return () => clearInterval(interval);
  }, []);

  const fetchDevices = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/devices`);
      setDevices(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching devices:', error);
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

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Devices
      </Typography>

      <Grid container spacing={3}>
        {devices.length === 0 ? (
          <Grid item xs={12}>
            <Paper sx={{ p: 3, textAlign: 'center' }}>
              <Typography color="textSecondary">No devices found</Typography>
            </Paper>
          </Grid>
        ) : (
          devices.map((device) => (
            <Grid item xs={12} sm={6} md={4} key={device.device_id}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    {device.device_id}
                  </Typography>
                  <Typography color="textSecondary" gutterBottom>
                    Location: {device.location || 'Unknown'}
                  </Typography>
                  <Box sx={{ mt: 2 }}>
                    <Chip
                      label={device.status}
                      color={device.status === 'online' ? 'success' : 'default'}
                      sx={{ mr: 1 }}
                    />
                  </Box>
                  <Typography variant="body2" color="textSecondary" sx={{ mt: 2 }}>
                    Last seen: {format(new Date(device.last_seen), 'PPpp')}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          ))
        )}
      </Grid>
    </Box>
  );
};

export default Devices;

