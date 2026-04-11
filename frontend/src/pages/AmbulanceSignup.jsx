// src/pages/AmbulanceSignup.jsx
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ambulanceSignup } from '../api';
import './SignupPage.css';

function AmbulanceSignup() {
  const [formData, setFormData] = useState({
    driver_name: '',
    ambulance_number: '',
    password: '',
    confirm_password: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (formData.password !== formData.confirm_password) {
      setError('Passwords do not match');
      return;
    }

    setLoading(true);
    try {
      const response = await ambulanceSignup(formData);
      localStorage.setItem('token', response.access_token);
      localStorage.setItem('role', response.role);
      localStorage.setItem('user', JSON.stringify(response.user_data));
      navigate('/ambulance/dashboard');
    } catch (err) {
      setError(err.response?.data?.detail || 'Signup failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="signup-container">
      <div className="signup-card">
        <h1 className="signup-title">🚑 Ambulance Signup</h1>
        <p className="signup-subtitle">Register your ambulance service</p>

        {error && <div className="error-message">{error}</div>}

        <form onSubmit={handleSubmit} className="signup-form">
          <div className="form-group">
            <label>Driver Name</label>
            <input
              type="text"
              value={formData.driver_name}
              onChange={(e) => setFormData({ ...formData, driver_name: e.target.value })}
              placeholder="Enter driver name"
              required
              minLength={2}
            />
          </div>

          <div className="form-group">
            <label>Ambulance Number</label>
            <input
              type="text"
              value={formData.ambulance_number}
              onChange={(e) => setFormData({ ...formData, ambulance_number: e.target.value })}
              placeholder="Enter ambulance number"
              required
              minLength={3}
            />
          </div>

          <div className="form-group">
            <label>Password</label>
            <input
              type="password"
              value={formData.password}
              onChange={(e) => setFormData({ ...formData, password: e.target.value })}
              placeholder="Enter password"
              required
              minLength={6}
            />
          </div>

          <div className="form-group">
            <label>Confirm Password</label>
            <input
              type="password"
              value={formData.confirm_password}
              onChange={(e) => setFormData({ ...formData, confirm_password: e.target.value })}
              placeholder="Confirm password"
              required
              minLength={6}
            />
          </div>

          <button type="submit" className="signup-btn" disabled={loading}>
            {loading ? 'Creating Account...' : 'Sign Up'}
          </button>

          <p className="login-link">
            Already have an account? <a href="/login">Login</a>
          </p>
        </form>
      </div>
    </div>
  );
}

export default AmbulanceSignup;
