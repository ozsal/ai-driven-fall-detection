import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  CircularProgress,
  TextField,
  Button
} from '@mui/material';
import axios from 'axios';
import { API_BASE_URL } from '../config';
import { format } from 'date-fns';

const FallEvents = () => {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('');

  useEffect(() => {
    fetchEvents();
    const interval = setInterval(fetchEvents, 10000); // Refresh every 10 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchEvents = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/fall-events?limit=100`);
      setEvents(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching events:', error);
      setLoading(false);
    }
  };

  const getSeverityColor = (score) => {
    if (score >= 7) return 'error';
    if (score >= 4) return 'warning';
    return 'success';
  };

  const getSeverityLabel = (score) => {
    if (score >= 7) return 'High';
    if (score >= 4) return 'Medium';
    return 'Low';
  };

  const filteredEvents = events.filter(event =>
    event.user_id?.toLowerCase().includes(filter.toLowerCase()) ||
    event.location?.toLowerCase().includes(filter.toLowerCase())
  );

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
        Fall Events
      </Typography>

      <Box sx={{ mb: 2, display: 'flex', gap: 2 }}>
        <TextField
          label="Filter by User or Location"
          variant="outlined"
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          sx={{ flexGrow: 1 }}
        />
        <Button variant="contained" onClick={fetchEvents}>
          Refresh
        </Button>
      </Box>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Timestamp</TableCell>
              <TableCell>User ID</TableCell>
              <TableCell>Location</TableCell>
              <TableCell>Severity</TableCell>
              <TableCell>Score</TableCell>
              <TableCell>Verified</TableCell>
              <TableCell>Status</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {filteredEvents.length === 0 ? (
              <TableRow>
                <TableCell colSpan={7} align="center">
                  No events found
                </TableCell>
              </TableRow>
            ) : (
              filteredEvents.map((event) => (
                <TableRow key={event._id}>
                  <TableCell>
                    {format(new Date(event.timestamp), 'PPpp')}
                  </TableCell>
                  <TableCell>{event.user_id}</TableCell>
                  <TableCell>{event.location || 'Unknown'}</TableCell>
                  <TableCell>
                    <Chip
                      label={getSeverityLabel(event.severity_score)}
                      color={getSeverityColor(event.severity_score)}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>{event.severity_score.toFixed(2)}/10</TableCell>
                  <TableCell>{event.verified ? 'Yes' : 'No'}</TableCell>
                  <TableCell>
                    {event.acknowledged ? (
                      <Chip label="Acknowledged" color="success" size="small" />
                    ) : (
                      <Chip label="Pending" color="warning" size="small" />
                    )}
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
};

export default FallEvents;

