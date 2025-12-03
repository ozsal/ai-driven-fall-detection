import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Box
} from '@mui/material';
import WarningIcon from '@mui/icons-material/Warning';

const Navbar = () => {
  const location = useLocation();

  return (
    <AppBar position="static">
      <Toolbar>
        <WarningIcon sx={{ mr: 2 }} />
        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
          Fall Detection System
        </Typography>
        <Box>
          <Button
            color="inherit"
            component={Link}
            to="/"
            sx={{ fontWeight: location.pathname === '/' ? 'bold' : 'normal' }}
          >
            Dashboard
          </Button>
          <Button
            color="inherit"
            component={Link}
            to="/events"
            sx={{ fontWeight: location.pathname === '/events' ? 'bold' : 'normal' }}
          >
            Events
          </Button>
          <Button
            color="inherit"
            component={Link}
            to="/devices"
            sx={{ fontWeight: location.pathname === '/devices' ? 'bold' : 'normal' }}
          >
            Devices
          </Button>
          <Button
            color="inherit"
            component={Link}
            to="/settings"
            sx={{ fontWeight: location.pathname === '/settings' ? 'bold' : 'normal' }}
          >
            Settings
          </Button>
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default Navbar;

