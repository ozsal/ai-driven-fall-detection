
// src/components/EnvironmentCharts.jsx
import React, { useEffect, useState } from "react";
import { Line } from "react-chartjs-2";
import { ref, onValue } from "firebase/database";
import { db } from "../firebase";

const EnvironmentCharts = () => {
  const [tempData, setTempData] = useState([]);
  const [humidityData, setHumidityData] = useState([]);
  const [labels, setLabels] = useState([]);

  useEffect(() => {
    const envRef = ref(db, "environment_updates");
    onValue(envRef, (snapshot) => {
      const data = snapshot.val();
      if (data) {
        const entries = Object.values(data);
        setLabels(entries.map((e) => e.timestamp));
        setTempData(entries.map((e) => e.temperature));
        setHumidityData(entries.map((e) => e.humidity));
      }
    });
  }, []);

  const chartData = {
    labels,
    datasets: [
      {
        label: "Temperature (°C)",
        data: tempData,
        borderColor: "rgba(255,99,132,1)",
        fill: false,
      },
      {
        label: "Humidity (%)",
        data: humidityData,
        borderColor: "rgba(54,162,235,1)",
        fill: false,
      },
    ],
  };

  return <Line data={chartData} />;
};

export default EnvironmentCharts;
