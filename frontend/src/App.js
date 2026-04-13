// src/App.js
import React from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import LoginPage from "./pages/LoginPage";
import AmbulanceSignup from "./pages/AmbulanceSignup";
import HospitalSignup from "./pages/HospitalSignup";
import AmbulanceDashboard from "./pages/AmbulanceDashboard";
import HospitalDashboard from "./pages/HospitalDashboard";
import AdminDashboard from "./pages/AdminDashboard";
import "./App.css";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Navigate to="/login" />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/ambulance/signup" element={<AmbulanceSignup />} />
        <Route path="/hospital/signup" element={<HospitalSignup />} />
        <Route path="/ambulance/dashboard" element={<AmbulanceDashboard />} />
        <Route path="/hospital/dashboard" element={<HospitalDashboard />} />
        <Route path="/admin/analytics" element={<AdminDashboard />} />
      </Routes>
    </Router>
  );
}

export default App;
