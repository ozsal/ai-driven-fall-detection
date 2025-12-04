
// src/pages/Dashboard.jsx
import React from "react";
import Navbar from "../components/Navbar";
import Sidebar from "../components/Sidebar";
import FallAlerts from "../components/FallAlerts";
import EnvironmentCharts from "../components/EnvironmentCharts";
import MotionLogs from "../components/MotionLogs";
import { Box, Grid } from "@mui/material";

const Dashboard = () => {
  return (
    <Box sx={{ display: "flex" }}>
      <Sidebar />
      <Box sx={{ flexGrow: 1 }}>
        <Navbar />
        <Grid container spacing={2} sx={{ p: 2 }}>
          <Grid item xs={12} md={6}>
            <FallAlerts />
          </Grid>
          <Grid item xs={12} md={6}>
            <EnvironmentCharts />
          </Grid>
          <Grid item xs={12}>
            <MotionLogs />
          </Grid>
        </Grid>
      </Box>
    </Box>
  );
};

export default Dashboard;
