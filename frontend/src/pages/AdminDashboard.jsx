// src/pages/AdminDashboard.jsx
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getAnalytics } from '../api';
import './AdminDashboard.css';

function AdminDashboard() {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const userData = localStorage.getItem('user');
    const role = localStorage.getItem('role');
    
    if (!userData || role !== 'hospital') {
      navigate('/login');
      return;
    }
    
    setUser(JSON.parse(userData));
    loadAnalytics();
    
    // Auto-refresh every 30 seconds
    const interval = setInterval(loadAnalytics, 30000);
    return () => clearInterval(interval);
  }, [navigate]);

  const loadAnalytics = async () => {
    try {
      const data = await getAnalytics();
      setAnalytics(data);
    } catch (err) {
      console.error('Failed to load analytics:', err);
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

  if (!user || loading) {
    return <div className="loading">Loading analytics...</div>;
  }

  return (
    <div className="admin-dashboard">
      <header className="dashboard-header">
        <div className="header-content">
          <h1>📊 Analytics Dashboard</h1>
          <div className="user-info">
            <span>{user.hospital_name}</span>
            <button onClick={handleLogout} className="logout-btn">Logout</button>
          </div>
        </div>
      </header>

      <div className="dashboard-content">
        {/* KPI Cards */}
        <div className="kpi-grid">
          <div className="kpi-card">
            <div className="kpi-icon">📋</div>
            <div className="kpi-value">{analytics.total_cases}</div>
            <div className="kpi-label">Total Cases</div>
          </div>

          <div className="kpi-card">
            <div className="kpi-icon">📈</div>
            <div className="kpi-value">{analytics.cases_last_24h}</div>
            <div className="kpi-label">Last 24 Hours</div>
          </div>

          <div className="kpi-card">
            <div className="kpi-icon">⚡</div>
            <div className="kpi-value">{analytics.average_severity_score.toFixed(1)}</div>
            <div className="kpi-label">Avg Severity Score</div>
          </div>

          <div className="kpi-card">
            <div className="kpi-icon">{analytics.trend.split(' ')[0]}</div>
            <div className="kpi-value">{analytics.trend.split(' ')[1] || 'Stable'}</div>
            <div className="kpi-label">Trend</div>
          </div>
        </div>

        {/* Severity Distribution */}
        <div className="analytics-section">
          <h2>Cases by Severity</h2>
          <div className="severity-chart">
            {Object.entries(analytics.cases_by_severity).map(([severity, count]) => {
              const percentage = (count / analytics.total_cases * 100).toFixed(1);
              return (
                <div key={severity} className="severity-bar-container">
                  <div className="severity-bar-label">
                    <span>{severity}</span>
                    <span>{count} ({percentage}%)</span>
                  </div>
                  <div className="severity-bar-track">
                    <div
                      className="severity-bar-fill"
                      style={{
                        width: `${percentage}%`,
                        backgroundColor: getSeverityColor(severity)
                      }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Peak Hours */}
        <div className="analytics-section">
          <h2>Peak Hours</h2>
          <div className="peak-hours-grid">
            {analytics.peak_hours.map((item, index) => (
              <div key={index} className="peak-hour-card">
                <div className="peak-hour-time">
                  {item.hour}:00 - {item.hour + 1}:00
                </div>
                <div className="peak-hour-count">{item.cases} cases</div>
                <div className="peak-hour-rank">#{index + 1}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Insights */}
        <div className="analytics-section">
          <h2>Insights</h2>
          <div className="insights-grid">
            <div className="insight-card">
              <div className="insight-icon">🔥</div>
              <div className="insight-content">
                <h3>Busiest Hour</h3>
                <p>
                  {analytics.peak_hours[0]?.hour}:00 with {analytics.peak_hours[0]?.cases} cases
                </p>
              </div>
            </div>

            <div className="insight-card">
              <div className="insight-icon">📊</div>
              <div className="insight-content">
                <h3>Most Common Severity</h3>
                <p>
                  {Object.entries(analytics.cases_by_severity)
                    .sort((a, b) => b[1] - a[1])[0]?.[0] || 'N/A'}
                </p>
              </div>
            </div>

            <div className="insight-card">
              <div className="insight-icon">⏱️</div>
              <div className="insight-content">
                <h3>24h Activity</h3>
                <p>{analytics.trend}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default AdminDashboard;
