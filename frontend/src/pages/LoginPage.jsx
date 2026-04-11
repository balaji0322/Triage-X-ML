// src/pages/LoginPage.jsx
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ambulanceLogin, hospitalLogin } from '../api';
import './LoginPage.css';

function LoginPage() {
  const [activeTab, setActiveTab] = useState('ambulance');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  // Ambulance form state
  const [ambulanceData, setAmbulanceData] = useState({
    ambulance_number: '',
    password: ''
  });

  // Hospital form state
  const [hospitalData, setHospitalData] = useState({
    hospital_id: '',
    password: ''
  });

  const handleAmbulanceLogin = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await ambulanceLogin(ambulanceData);
      localStorage.setItem('token', response.access_token);
      localStorage.setItem('role', response.role);
      localStorage.setItem('user', JSON.stringify(response.user_data));
      navigate('/ambulance/dashboard');
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  const handleHospitalLogin = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await hospitalLogin(hospitalData);
      localStorage.setItem('token', response.access_token);
      localStorage.setItem('role', response.role);
      localStorage.setItem('user', JSON.stringify(response.user_data));
      navigate('/hospital/dashboard');
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <h1 className="login-title">🏥 TRIAGE-X</h1>
        <p className="login-subtitle">Emergency Triage System</p>

        <div className="tab-buttons">
          <button
            className={`tab-btn ${activeTab === 'ambulance' ? 'active' : ''}`}
            onClick={() => setActiveTab('ambulance')}
          >
            🚑 Ambulance
          </button>
          <button
            className={`tab-btn ${activeTab === 'hospital' ? 'active' : ''}`}
            onClick={() => setActiveTab('hospital')}
          >
            🏥 Hospital
          </button>
        </div>

        {error && <div className="error-message">{error}</div>}

        {activeTab === 'ambulance' ? (
          <form onSubmit={handleAmbulanceLogin} className="login-form">
            <div className="form-group">
              <label>Ambulance Number</label>
              <input
                type="text"
                value={ambulanceData.ambulance_number}
                onChange={(e) => setAmbulanceData({ ...ambulanceData, ambulance_number: e.target.value })}
                placeholder="Enter ambulance number"
                required
              />
            </div>
            <div className="form-group">
              <label>Password</label>
              <input
                type="password"
                value={ambulanceData.password}
                onChange={(e) => setAmbulanceData({ ...ambulanceData, password: e.target.value })}
                placeholder="Enter password"
                required
              />
            </div>
            <button type="submit" className="login-btn" disabled={loading}>
              {loading ? 'Logging in...' : 'Login'}
            </button>
            <p className="signup-link">
              Don't have an account? <a href="/ambulance/signup">Sign up</a>
            </p>
          </form>
        ) : (
          <form onSubmit={handleHospitalLogin} className="login-form">
            <div className="form-group">
              <label>Hospital ID</label>
              <input
                type="text"
                value={hospitalData.hospital_id}
                onChange={(e) => setHospitalData({ ...hospitalData, hospital_id: e.target.value })}
                placeholder="Enter hospital ID"
                required
              />
            </div>
            <div className="form-group">
              <label>Password</label>
              <input
                type="password"
                value={hospitalData.password}
                onChange={(e) => setHospitalData({ ...hospitalData, password: e.target.value })}
                placeholder="Enter password"
                required
              />
            </div>
            <button type="submit" className="login-btn" disabled={loading}>
              {loading ? 'Logging in...' : 'Login'}
            </button>
            <p className="signup-link">
              Don't have an account? <a href="/hospital/signup">Sign up</a>
            </p>
          </form>
        )}
      </div>
    </div>
  );
}

export default LoginPage;
