// src/pages/HospitalSignup.jsx
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { hospitalSignup } from '../api';
import './SignupPage.css';

function HospitalSignup() {
  const [formData, setFormData] = useState({
    hospital_name: '',
    address: '',
    password: '',
    confirm_password: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [hospitalId, setHospitalId] = useState('');
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
      const response = await hospitalSignup(formData);
      setHospitalId(response.user_data.hospital_id);
      
      // Show hospital ID for 3 seconds before redirecting
      setTimeout(() => {
        localStorage.setItem('token', response.access_token);
        localStorage.setItem('role', response.role);
        localStorage.setItem('user', JSON.stringify(response.user_data));
        navigate('/hospital/dashboard');
      }, 3000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Signup failed');
      setLoading(false);
    }
  };

  if (hospitalId) {
    return (
      <div className="signup-container">
        <div className="signup-card success-card">
          <h1 className="success-title">✅ Registration Successful!</h1>
          <div className="hospital-id-display">
            <p>Your Hospital ID:</p>
            <h2 className="hospital-id">{hospitalId}</h2>
            <p className="id-note">Please save this ID for login</p>
          </div>
          <p className="redirect-note">Redirecting to dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="signup-container">
      <div className="signup-card">
        <h1 className="signup-title">🏥 Hospital Signup</h1>
        <p className="signup-subtitle">Register your hospital</p>

        {error && <div className="error-message">{error}</div>}

        <form onSubmit={handleSubmit} className="signup-form">
          <div className="form-group">
            <label>Hospital Name</label>
            <input
              type="text"
              value={formData.hospital_name}
              onChange={(e) => setFormData({ ...formData, hospital_name: e.target.value })}
              placeholder="Enter hospital name"
              required
              minLength={3}
            />
          </div>

          <div className="form-group">
            <label>Address</label>
            <textarea
              value={formData.address}
              onChange={(e) => setFormData({ ...formData, address: e.target.value })}
              placeholder="Enter hospital address"
              required
              minLength={5}
              rows={3}
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

export default HospitalSignup;
