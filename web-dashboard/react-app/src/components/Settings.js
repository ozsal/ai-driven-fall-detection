import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  Grid,
  Switch,
  FormControlLabel,
  Alert
} from '@mui/material';

const Settings = () => {
  const [settings, setSettings] = useState({
    emailAlerts: true,
    pushNotifications: true,
    alertThreshold: 5.0,
    emailAddress: '',
    phoneNumber: ''
  });
  const [saved, setSaved] = useState(false);

  const handleChange = (field, value) => {
    setSettings(prev => ({ ...prev, [field]: value }));
    setSaved(false);
  };

  const handleSave = () => {
    // In production, save to backend
    console.log('Saving settings:', settings);
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Settings
      </Typography>

      {saved && (
        <Alert severity="success" sx={{ mb: 3 }}>
          Settings saved successfully!
        </Alert>
      )}

      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>
          Notification Preferences
        </Typography>
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <FormControlLabel
              control={
                <Switch
                  checked={settings.emailAlerts}
                  onChange={(e) => handleChange('emailAlerts', e.target.checked)}
                />
              }
              label="Email Alerts"
            />
          </Grid>
          <Grid item xs={12}>
            <FormControlLabel
              control={
                <Switch
                  checked={settings.pushNotifications}
                  onChange={(e) => handleChange('pushNotifications', e.target.checked)}
                />
              }
              label="Push Notifications"
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Alert Threshold"
              type="number"
              value={settings.alertThreshold}
              onChange={(e) => handleChange('alertThreshold', parseFloat(e.target.value))}
              helperText="Minimum severity score to trigger alerts (0-10)"
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Email Address"
              type="email"
              value={settings.emailAddress}
              onChange={(e) => handleChange('emailAddress', e.target.value)}
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Phone Number"
              type="tel"
              value={settings.phoneNumber}
              onChange={(e) => handleChange('phoneNumber', e.target.value)}
            />
          </Grid>
          <Grid item xs={12}>
            <Button variant="contained" onClick={handleSave}>
              Save Settings
            </Button>
          </Grid>
        </Grid>
      </Paper>
    </Box>
  );
};

export default Settings;



