// src/pages/HospitalDashboard.jsx
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getCases, getHospitalStats } from '../api';
import './HospitalDashboard.css';

function HospitalDashboard() {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [cases, setCases] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    const userData = localStorage.getItem('user');
    const role = localStorage.getItem('role');
    
    if (!userData || role !== 'hospital') {
      navigate('/login');
      return;
    }
    
    setUser(JSON.parse(userData));
    loadData();
    
    // Auto-refresh every 10 seconds
    const interval = setInterval(loadData, 10000);
    return () => clearInterval(interval);
  }, [navigate]);

  const loadData = async () => {
    try {
      const [casesData, statsData] = await Promise.all([
        getCases(),
        getHospitalStats()
      ]);
      setCases(casesData);
      setStats(statsData);
    } catch (err) {
      console.error('Failed to load data:', err);
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

  const filteredCases = filter === 'all' 
    ? cases 
    : cases.filter(c => c.severity === filter);

  if (!user) return null;

  return (
    <div className="dashboard-container">
      <header className="dashboard-header">
        <div className="header-content">
          <h1>🏥 Hospital Dashboard</h1>
          <div className="user-info">
            <span>{user.hospital_name} ({user.hospital_id})</span>
            <button onClick={handleLogout} className="logout-btn">Logout</button>
          </div>
        </div>
      </header>

      <div className="dashboard-content">
        {loading ? (
          <div className="loading">Loading...</div>
        ) : (
          <>
            {/* Stats Cards */}
            {stats && (
              <div className="stats-grid">
                <div className="stat-card" style={{ borderLeft: `4px solid ${getSeverityColor('Immediate')}` }}>
                  <div className="stat-value">{stats.Immediate}</div>
                  <div className="stat-label">Immediate</div>
                </div>
                <div className="stat-card" style={{ borderLeft: `4px solid ${getSeverityColor('Urgent')}` }}>
                  <div className="stat-value">{stats.Urgent}</div>
                  <div className="stat-label">Urgent</div>
                </div>
                <div className="stat-card" style={{ borderLeft: `4px solid ${getSeverityColor('Moderate')}` }}>
                  <div className="stat-value">{stats.Moderate}</div>
                  <div className="stat-label">Moderate</div>
                </div>
                <div className="stat-card" style={{ borderLeft: `4px solid ${getSeverityColor('Minor')}` }}>
                  <div className="stat-value">{stats.Minor}</div>
                  <div className="stat-label">Minor</div>
                </div>
                <div className="stat-card" style={{ borderLeft: '4px solid #667eea' }}>
                  <div className="stat-value">{stats.total}</div>
                  <div className="stat-label">Total Cases</div>
                </div>
              </div>
            )}

            {/* Filter Buttons */}
            <div className="filter-section">
              <button
                className={`filter-btn ${filter === 'all' ? 'active' : ''}`}
                onClick={() => setFilter('all')}
              >
                All Cases
              </button>
              <button
                className={`filter-btn ${filter === 'Immediate' ? 'active' : ''}`}
                onClick={() => setFilter('Immediate')}
                style={{ borderColor: getSeverityColor('Immediate') }}
              >
                Immediate
              </button>
              <button
                className={`filter-btn ${filter === 'Urgent' ? 'active' : ''}`}
                onClick={() => setFilter('Urgent')}
                style={{ borderColor: getSeverityColor('Urgent') }}
              >
                Urgent
              </button>
              <button
                className={`filter-btn ${filter === 'Moderate' ? 'active' : ''}`}
                onClick={() => setFilter('Moderate')}
                style={{ borderColor: getSeverityColor('Moderate') }}
              >
                Moderate
              </button>
              <button
                className={`filter-btn ${filter === 'Minor' ? 'active' : ''}`}
                onClick={() => setFilter('Minor')}
                style={{ borderColor: getSeverityColor('Minor') }}
              >
                Minor
              </button>
            </div>

            {/* Cases Table */}
            <div className="card">
              <div className="card-header">
                <h2>Incoming Cases</h2>
                <button onClick={loadData} className="refresh-btn">🔄 Refresh</button>
              </div>

              {filteredCases.length === 0 ? (
                <p className="no-cases">No cases found</p>
              ) : (
                <div className="table-container">
                  <table className="cases-table">
                    <thead>
                      <tr>
                        <th>Time</th>
                        <th>Ambulance</th>
                        <th>Driver</th>
                        <th>Age</th>
                        <th>Vitals</th>
                        <th>Severity</th>
                        <th>Confidence</th>
                      </tr>
                    </thead>
                    <tbody>
                      {filteredCases.map((c) => (
                        <tr
                          key={c.case_id}
                          className={c.severity === 'Immediate' ? 'critical-row' : ''}
                        >
                          <td>{new Date(c.timestamp).toLocaleString()}</td>
                          <td>{c.ambulance_number}</td>
                          <td>{c.driver_name}</td>
                          <td>{c.patient_data.age}</td>
                          <td className="vitals-cell">
                            <div>HR: {c.patient_data.heart_rate}</div>
                            <div>BP: {c.patient_data.systolic_bp}/{c.patient_data.diastolic_bp}</div>
                            <div>SpO2: {c.patient_data.oxygen_saturation}%</div>
                          </td>
                          <td>
                            <span
                              className="severity-badge"
                              style={{ backgroundColor: getSeverityColor(c.severity) }}
                            >
                              {c.severity}
                            </span>
                          </td>
                          <td>{(c.confidence * 100).toFixed(1)}%</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  );
}

export default HospitalDashboard;
