// src/pages/HospitalDashboard.jsx
import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  getCases, 
  getHospitalStats, 
  WebSocketManager,
  getAmbulanceLocations,
  LocationWebSocketManager,
  updateICUBeds,
  getICUStatus
} from '../api';
import HospitalTrackingMap from '../components/HospitalTrackingMap';
import './HospitalDashboard.css';

function HospitalDashboard() {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [cases, setCases] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');
  const [wsConnected, setWsConnected] = useState(false);
  const wsManager = useRef(null);
  
  // Location tracking state
  const [ambulanceLocations, setAmbulanceLocations] = useState([]);
  const [showMap, setShowMap] = useState(true);
  const locationWsRef = useRef(null);
  
  // ICU management state
  const [icuData, setIcuData] = useState({
    icu_total: 0,
    icu_available: 0,
    icu_occupied: 0,
    occupancy_rate: 0
  });
  const [icuFormData, setIcuFormData] = useState({
    icu_total: '',
    icu_available: ''
  });
  const [icuUpdateSuccess, setIcuUpdateSuccess] = useState('');
  const [icuUpdateError, setIcuUpdateError] = useState('');

  useEffect(() => {
    const userData = localStorage.getItem('user');
    const role = localStorage.getItem('role');
    
    if (!userData || role !== 'hospital') {
      navigate('/login');
      return;
    }
    
    setUser(JSON.parse(userData));
    loadData();
    loadICUData(JSON.parse(userData).hospital_id);
    
    // 🚀 FEATURE 1: Initialize WebSocket connection
    wsManager.current = new WebSocketManager('hospital');
    wsManager.current.connect(
      (message) => {
        console.log('📨 WebSocket message received:', message);
        
        if (message.type === 'connection') {
          setWsConnected(true);
        } else if (message.type === 'new_case') {
          // Add new case to the list
          setCases(prevCases => [message.case, ...prevCases]);
          // Reload stats
          loadStats();
          // Show notification
          showNotification(message.case);
        } else if (message.type === 'icu_update') {
          // Update ICU data in real-time
          if (message.hospital_id === JSON.parse(userData).hospital_id) {
            setIcuData({
              icu_total: message.icu_total,
              icu_available: message.icu_available,
              icu_occupied: message.icu_occupied,
              occupancy_rate: message.occupancy_rate
            });
          }
        }
      },
      (error) => {
        console.error('❌ WebSocket error:', error);
        setWsConnected(false);
      }
    );
    
    // Fallback: Polling every 10 seconds if WebSocket fails
    const pollingInterval = setInterval(() => {
      if (!wsConnected) {
        console.log('🔄 Polling for updates (WebSocket not connected)');
        loadData();
      }
    }, 10000);
    
    // Initialize location tracking WebSocket
    initializeLocationTracking();
    
    return () => {
      clearInterval(pollingInterval);
      if (wsManager.current) {
        wsManager.current.disconnect();
      }
      if (locationWsRef.current) {
        locationWsRef.current.disconnect();
      }
    };
  }, [navigate, wsConnected]);
  
  // Initialize location tracking
  const initializeLocationTracking = async () => {
    try {
      // Get initial ambulance locations
      const locations = await getAmbulanceLocations();
      setAmbulanceLocations(locations);
      
      // Connect to location WebSocket
      locationWsRef.current = new LocationWebSocketManager('hospital');
      locationWsRef.current.connect(
        (message) => {
          if (message.type === 'location_update') {
            // Update ambulance location in real-time
            setAmbulanceLocations(prev => {
              const updated = prev.filter(
                amb => amb.ambulance_id !== message.ambulance_id
              );
              return [...updated, {
                ambulance_id: message.ambulance_id,
                ...message.location,
                timestamp: message.timestamp
              }];
            });
          }
        },
        (error) => {
          console.error('Location WebSocket error:', error);
        }
      );
    } catch (err) {
      console.error('Failed to initialize location tracking:', err);
    }
  };

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

  const loadStats = async () => {
    try {
      const statsData = await getHospitalStats();
      setStats(statsData);
    } catch (err) {
      console.error('Failed to load stats:', err);
    }
  };
  
  const loadICUData = async (hospitalId) => {
    try {
      const data = await getICUStatus(hospitalId);
      setIcuData({
        icu_total: data.icu_total,
        icu_available: data.icu_available,
        icu_occupied: data.icu_occupied,
        occupancy_rate: data.occupancy_rate
      });
      setIcuFormData({
        icu_total: data.icu_total.toString(),
        icu_available: data.icu_available.toString()
      });
    } catch (err) {
      console.error('Failed to load ICU data:', err);
    }
  };
  
  const handleICUUpdate = async (e) => {
    e.preventDefault();
    setIcuUpdateError('');
    setIcuUpdateSuccess('');
    
    try {
      const result = await updateICUBeds(
        user.hospital_id,
        parseInt(icuFormData.icu_total),
        parseInt(icuFormData.icu_available)
      );
      
      setIcuData({
        icu_total: result.icu_total,
        icu_available: result.icu_available,
        icu_occupied: result.icu_occupied,
        occupancy_rate: result.occupancy_rate
      });
      
      setIcuUpdateSuccess('✅ ICU beds updated successfully!');
      setTimeout(() => setIcuUpdateSuccess(''), 3000);
    } catch (err) {
      setIcuUpdateError(err.response?.data?.detail || 'Failed to update ICU beds');
    }
  };

  const showNotification = (caseData) => {
    // Show browser notification if permitted
    if ('Notification' in window && Notification.permission === 'granted') {
      new Notification('🚨 New Emergency Case', {
        body: `${caseData.severity} case from ${caseData.ambulance_number}`,
        icon: '/favicon.ico'
      });
    }
    
    // Play sound for urgent cases
    if (caseData.severity === 'Urgent' || caseData.severity === 'Immediate') {
      const audio = new Audio('/notification.mp3');
      audio.play().catch(e => console.log('Audio play failed:', e));
    }
  };

  const handleLogout = () => {
    if (wsManager.current) {
      wsManager.current.disconnect();
    }
    localStorage.clear();
    navigate('/login');
  };

  const navigateToAnalytics = () => {
    navigate('/admin/analytics');
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
            <span className={`ws-indicator ${wsConnected ? 'connected' : 'disconnected'}`}>
              {wsConnected ? '🟢 Live' : '🔴 Polling'}
            </span>
            <button onClick={navigateToAnalytics} className="analytics-btn">
              📊 Analytics
            </button>
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

            {/* ICU Bed Management */}
            <div className="card icu-management-card">
              <div className="card-header">
                <h2>🏥 ICU Bed Management</h2>
              </div>
              
              <div className="icu-content">
                {/* Current ICU Status */}
                <div className="icu-status">
                  <h3>Current Status</h3>
                  <div className="icu-stats-grid">
                    <div className="icu-stat">
                      <div className="icu-stat-value">{icuData.icu_total}</div>
                      <div className="icu-stat-label">Total ICU Beds</div>
                    </div>
                    <div className="icu-stat">
                      <div className="icu-stat-value" style={{ color: '#22c55e' }}>{icuData.icu_available}</div>
                      <div className="icu-stat-label">Available</div>
                    </div>
                    <div className="icu-stat">
                      <div className="icu-stat-value" style={{ color: '#ef4444' }}>{icuData.icu_occupied}</div>
                      <div className="icu-stat-label">Occupied</div>
                    </div>
                    <div className="icu-stat">
                      <div className="icu-stat-value">{icuData.occupancy_rate}%</div>
                      <div className="icu-stat-label">Occupancy Rate</div>
                    </div>
                  </div>
                </div>
                
                {/* Update ICU Form */}
                <div className="icu-update-form">
                  <h3>Update ICU Availability</h3>
                  {icuUpdateSuccess && <div className="alert alert-success">{icuUpdateSuccess}</div>}
                  {icuUpdateError && <div className="alert alert-error">{icuUpdateError}</div>}
                  
                  <form onSubmit={handleICUUpdate}>
                    <div className="form-row">
                      <div className="form-field">
                        <label>Total ICU Beds</label>
                        <input
                          type="number"
                          value={icuFormData.icu_total}
                          onChange={(e) => setIcuFormData({ ...icuFormData, icu_total: e.target.value })}
                          required
                          min="0"
                        />
                      </div>
                      <div className="form-field">
                        <label>Available ICU Beds</label>
                        <input
                          type="number"
                          value={icuFormData.icu_available}
                          onChange={(e) => setIcuFormData({ ...icuFormData, icu_available: e.target.value })}
                          required
                          min="0"
                          max={icuFormData.icu_total}
                        />
                      </div>
                    </div>
                    <button type="submit" className="update-icu-btn">
                      🔄 Update ICU Beds
                    </button>
                  </form>
                </div>
              </div>
            </div>

            {/* Real-Time Ambulance Tracking Map */}
            <div className="card map-card">
              <div className="card-header">
                <h2>🗺️ Real-Time Ambulance Tracking</h2>
                <button 
                  onClick={() => setShowMap(!showMap)} 
                  className="toggle-map-btn"
                >
                  {showMap ? '📊 Show Table' : '🗺️ Show Map'}
                </button>
              </div>
              
              {showMap && (
                <HospitalTrackingMap
                  ambulances={ambulanceLocations}
                  hospitalLocation={user ? {
                    latitude: user.latitude || 13.0827,
                    longitude: user.longitude || 80.2707,
                    name: user.hospital_name
                  } : null}
                />
              )}
            </div>

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
