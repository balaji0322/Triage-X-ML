// src/components/ResultCard.jsx
import React from "react";
import "./ResultCard.css";

const COLORS = {
  Immediate: "#ff4d4d",
  Urgent: "#ff9500",
  Moderate: "#ffd200",
  Minor: "#4caf50",
};

export default function ResultCard({ severity, confidence }) {
  const bg = COLORS[severity] || "#777";
  
  return (
    <div className="result-card" style={{ backgroundColor: bg }}>
      <h2>{severity}</h2>
      <p>Confidence: <strong>{(confidence * 100).toFixed(1)}%</strong></p>
    </div>
  );
}
