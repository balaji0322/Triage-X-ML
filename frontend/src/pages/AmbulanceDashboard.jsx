// src/pages/AmbulanceDashboard.jsx
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { predictSeverity, sendCase, getAmbulanceRecentCases } from '../api';
import './AmbulanceDashboard.css';

function AmbulanceDashboard() {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(false);
  const [prediction, setPrediction] = useState(null);
  const [recentCases, setRecentCases] = useState([]);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const [patientData, setPatientData] = useState({
    heart_rate: '',
    systolic_bp: '',
    diastolic_bp: '',
    oxygen_saturation: '',
    temperature: '',
    respiratory_rate: '',
    age: '',
    gender: 'male',
    chest_pain: 0,
    fever: 0,
    breathing_difficulty: 0,
    injury_type: 0,
    diabetes: 0,
    heart_disease: 0,
    hypertension: 0,
    asthma: 0
  });

  useEffect(() => {
    const userData = localStorage.getItem('user');
    const role = localStorage.getItem('role');
    
    if (!userData || role !== 'ambulance') {
      navigate('/login');
      return;
    }
    
    setUser(JSON.parse(userData));
    loadRecentCases();
  }, [navigate]);

  const loadRecentCases = async () => {
    try {
      const cases = await getAmbulanceRecentCases();
      setRecentCases(cases);
    } catch (err) {
      console.error('Failed to load recent cases:', err);
    }
  };

  const handlePredict = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const result = await predictSeverity(patientData);
      setPrediction(result);
    } catch (err) {
      setError(err.response?.data?.detail || 'Prediction failed');
    } finally {
      setLoading(false);
    }
  };

  const handleSendCase = async () => {
    if (!prediction) return;

    setLoading(true);
    setError('');
    setSuccess('');

    try {
      await sendCase({
        patient_data: patientData,
        severity: prediction.severity,
        confidence: prediction.confidence
      });
      setSuccess('Case sent successfully!');
      setPrediction(null);
      setPatientData({
        heart_rate: '',
        systolic_bp: '',
        diastolic_bp: '',
        oxygen_saturation: '',
        temperature: '',
        respiratory_rate: '',
        age: '',
        gender: 'male',
        chest_pain: 0,
        fever: 0,
        breathing_difficulty: 0,
        injury_type: 0,
        diabetes: 0,
        heart_disease: 0,
        hypertension: 0,
        asthma: 0
      });
      loadRecentCases();
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to send case');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.clear();
    navigate('/login');
  };

  const getSeverityColor = (severity) => {
    const colors = {
      'Immediate': '#ef4444',
      'Urgent': '#f97316',
      'Moderate': '#eab308',
      'Minor': '#22c55e'
    };
    return colors[severity] || '#666';
  };

  if (!user) return null;

  return (
    <div className="dashboard-container">
      <header className="dashboard-header">
        <div className="header-content">
          <h1>🚑 Ambulance Dashboard</h1>
          <div className="user-info">
            <span>{user.driver_name} ({user.ambulance_number})</span>
            <button onClick={handleLogout} className="logout-btn">Logout</button>
          </div>
        </div>
      </header>

      <div className="dashboard-content">
        {error && <div className="alert alert-error">{error}</div>}
        {success && <div className="alert alert-success">{success}</div>}

        <div className="dashboard-grid">
          {/* Patient Input Form */}
          <div className="card">
            <h2>Patient Information</h2>
            <form onSubmit={handlePredict} className="patient-form">
              <div className="form-row">
                <div className="form-field">
                  <label>Heart Rate (bpm)</label>
                  <input
                    type="number"
                    value={patientData.heart_rate}
                    onChange={(e) => setPatientData({ ...patientData, heart_rate: e.target.value })}
                    required
                    min="30"
                    max="250"
                  />
                </div>
                <div className="form-field">
                  <label>Systolic BP (mmHg)</label>
                  <input
                    type="number"
                    value={patientData.systolic_bp}
                    onChange={(e) => setPatientData({ ...patientData, systolic_bp: e.target.value })}
                    required
                    min="50"
                    max="250"
                  />
                </div>
              </div>

              <div className="form-row">
                <div className="form-field">
                  <label>Diastolic BP (mmHg)</label>
                  <input
                    type="number"
                    value={patientData.diastolic_bp}
                    onChange={(e) => setPatientData({ ...patientData, diastolic_bp: e.target.value })}
                    required
                    min="30"
                    max="150"
                  />
                </div>
                <div className="form-field">
                  <label>SpO2 (%)</label>
                  <input
                    type="number"
                    value={patientData.oxygen_saturation}
                    onChange={(e) => setPatientData({ ...patientData, oxygen_saturation: e.target.value })}
                    required
                    min="50"
                    max="100"
                  />
                </div>
              </div>

              <div className="form-row">
                <div className="form-field">
                  <label>Temperature (°C)</label>
                  <input
                    type="number"
                    step="0.1"
                    value={patientData.temperature}
                    onChange={(e) => setPatientData({ ...patientData, temperature: e.target.value })}
                    required
                    min="30"
                    max="45"
                  />
                </div>
                <div className="form-field">
                  <label>Respiratory Rate</label>
                  <input
                    type="number"
                    value={patientData.respiratory_rate}
                    onChange={(e) => setPatientData({ ...patientData, respiratory_rate: e.target.value })}
                    required
                    min="5"
                    max="60"
                  />
                </div>
              </div>

              <div className="form-row">
                <div className="form-field">
                  <label>Age</label>
                  <input
                    type="number"
                    value={patientData.age}
                    onChange={(e) => setPatientData({ ...patientData, age: e.target.value })}
                    required
                    min="0"
                    max="120"
                  />
                </div>
                <div className="form-field">
                  <label>Gender</label>
                  <select
                    value={patientData.gender}
                    onChange={(e) => setPatientData({ ...patientData, gender: e.target.value })}
                  >
                    <option value="male">Male</option>
                    <option value="female">Female</option>
                    <option value="other">Other</option>
                  </select>
                </div>
              </div>

              <div className="symptoms-section">
                <h3>Symptoms</h3>
                <div className="checkbox-grid">
                  {[
                    { key: 'chest_pain', label: 'Chest Pain' },
                    { key: 'fever', label: 'Fever' },
                    { key: 'breathing_difficulty', label: 'Breathing Difficulty' },
                    { key: 'injury_type', label: 'Traumatic Injury' }
                  ].map(({ key, label }) => (
                    <label key={key} className="checkbox-label">
                      <input
                        type="checkbox"
                        checked={patientData[key] === 1}
                        onChange={(e) => setPatientData({ ...patientData, [key]: e.target.checked ? 1 : 0 })}
                      />
                      {label}
                    </label>
                  ))}
                </div>
              </div>

              <div className="symptoms-section">
                <h3>Medical History</h3>
                <div className="checkbox-grid">
                  {[
                    { key: 'diabetes', label: 'Diabetes' },
                    { key: 'heart_disease', label: 'Heart Disease' },
                    { key: 'hypertension', label: 'Hypertension' },
                    { key: 'asthma', label: 'Asthma' }
                  ].map(({ key, label }) => (
                    <label key={key} className="checkbox-label">
                      <input
                        type="checkbox"
                        checked={patientData[key] === 1}
                        onChange={(e) => setPatientData({ ...patientData, [key]: e.target.checked ? 1 : 0 })}
                      />
                      {label}
                    </label>
                  ))}
                </div>
              </div>

              <button type="submit" className="predict-btn" disabled={loading}>
                {loading ? 'Predicting...' : '🔍 Predict Severity'}
              </button>
            </form>
          </div>

          {/* Prediction Result */}
          {prediction && (
            <div className="card prediction-card">
              <h2>Prediction Result</h2>
              <div
                className="severity-display"
                style={{ backgroundColor: getSeverityColor(prediction.severity) }}
              >
                <div className="severity-label">{prediction.severity}</div>
                <div className="confidence-label">
                  Confidence: {(prediction.confidence * 100).toFixed(1)}%
                </div>
              </div>
              <button onClick={handleSendCase} className="send-btn" disabled={loading}>
                {loading ? 'Sending...' : '📤 Send Case to Hospital'}
              </button>
            </div>
          )}

          {/* Recent Cases */}
          <div className="card recent-cases-card">
            <h2>Recent Cases</h2>
            {recentCases.length === 0 ? (
              <p className="no-cases">No cases yet</p>
            ) : (
              <div className="cases-list">
                {recentCases.map((c) => (
                  <div key={c.case_id} className="case-item">
                    <div
                      className="case-severity"
                      style={{ backgroundColor: getSeverityColor(c.severity) }}
                    >
                      {c.severity}
                    </div>
                    <div className="case-details">
                      <div>Age: {c.patient_data.age} | HR: {c.patient_data.heart_rate}</div>
                      <div className="case-time">
                        {new Date(c.timestamp).toLocaleString()}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default AmbulanceDashboard;
