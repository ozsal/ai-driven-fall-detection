
// src/components/FallAlerts.jsx
import React, { useEffect, useState } from "react";
import { ref, onValue } from "firebase/database";
import { db } from "../firebase";
import { Card, CardContent, Typography } from "@mui/material";

const FallAlerts = () => {
  const [alerts, setAlerts] = useState([]);

  useEffect(() => {
    const alertsRef = ref(db, "fall_events");
    onValue(alertsRef, (snapshot) => {
      const data = snapshot.val();
      if (data) {
        setAlerts(Object.values(data).reverse());
      }
    });
  }, []);

  return (
    <Card>
      <CardContent>
        <Typography variant="h6">Recent Fall Alerts</Typography>
        {alerts.slice(0, 5).map((alert, index) => (
          <Typography key={index}>
            {alert.timestamp} - {alert.status} (Confidence: {alert.confidence})
          </Typography>
        ))}
      </CardContent>
    </Card>
  );
};

export default FallAlerts;
