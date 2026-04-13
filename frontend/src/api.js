// src/api.js
import axios from "axios";

const API_BASE_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

// Create axios instance with auth interceptor
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 8000,
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.clear();
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// ============ ML PREDICTION (EXISTING) ============
export const predictSeverity = async (patientData) => {
  const response = await axios.post(`${API_BASE_URL}/predict`, patientData);
  return response.data;
};

export const getFeatureImportance = async () => {
  const response = await axios.get(`${API_BASE_URL}/feature_importance`);
  return response.data;
};

export const explainPrediction = async (patientData) => {
  const response = await axios.post(`${API_BASE_URL}/explain`, patientData);
  return response.data;
};

// ============ AUTHENTICATION ============
export const ambulanceSignup = async (data) => {
  const response = await axios.post(`${API_BASE_URL}/api/ambulance/signup`, data);
  return response.data;
};

export const ambulanceLogin = async (data) => {
  const response = await axios.post(`${API_BASE_URL}/api/ambulance/login`, data);
  return response.data;
};

export const hospitalSignup = async (data) => {
  const response = await axios.post(`${API_BASE_URL}/api/hospital/signup`, data);
  return response.data;
};

export const hospitalLogin = async (data) => {
  const response = await axios.post(`${API_BASE_URL}/api/hospital/login`, data);
  return response.data;
};

// ============ CASES ============
export const sendCase = async (data) => {
  const response = await api.post('/api/send-case', data);
  return response.data;
};

export const getCases = async () => {
  const response = await api.get('/api/cases');
  return response.data;
};

export const getAmbulanceRecentCases = async () => {
  const response = await api.get('/api/ambulance/recent-cases');
  return response.data;
};

export const getHospitalStats = async () => {
  const response = await api.get('/api/hospital/stats');
  return response.data;
};

// ============ ADVANCED FEATURES ============

// FEATURE 2: Smart Hospital Allocation
export const suggestHospital = async (data) => {
  const response = await api.post('/api/suggest-hospital', data);
  return response.data;
};

// FEATURE 3: Enhanced AI Insights
export const getEnhancedPrediction = async (patientData) => {
  const response = await api.post('/api/predict/enhanced', patientData);
  return response.data;
};

// FEATURE 4: Analytics Dashboard
export const getAnalytics = async () => {
  const response = await api.get('/api/analytics');
  return response.data;
};

// ============ WEBSOCKET ============

// FEATURE 1: WebSocket Connection Manager
export class WebSocketManager {
  constructor(role = 'hospital') {
    this.ws = null;
    this.role = role;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectDelay = 3000;
    this.listeners = [];
  }

  connect(onMessage, onError) {
    const wsUrl = API_BASE_URL.replace('http', 'ws');
    this.ws = new WebSocket(`${wsUrl}/ws/cases?role=${this.role}`);

    this.ws.onopen = () => {
      console.log('✅ WebSocket connected');
      this.reconnectAttempts = 0;
      
      // Send ping every 30 seconds to keep connection alive
      this.pingInterval = setInterval(() => {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
          this.ws.send('ping');
        }
      }, 30000);
    };

    this.ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        console.log('📨 WebSocket message:', data);
        
        // Call all registered listeners
        this.listeners.forEach(listener => listener(data));
        
        if (onMessage) {
          onMessage(data);
        }
      } catch (error) {
        console.error('❌ WebSocket message parse error:', error);
      }
    };

    this.ws.onerror = (error) => {
      console.error('❌ WebSocket error:', error);
      if (onError) {
        onError(error);
      }
    };

    this.ws.onclose = () => {
      console.log('🔌 WebSocket disconnected');
      clearInterval(this.pingInterval);
      
      // Attempt to reconnect
      if (this.reconnectAttempts < this.maxReconnectAttempts) {
        this.reconnectAttempts++;
        console.log(`🔄 Reconnecting... (Attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
        setTimeout(() => {
          this.connect(onMessage, onError);
        }, this.reconnectDelay);
      }
    };
  }

  addListener(callback) {
    this.listeners.push(callback);
  }

  removeListener(callback) {
    this.listeners = this.listeners.filter(l => l !== callback);
  }

  disconnect() {
    if (this.ws) {
      clearInterval(this.pingInterval);
      this.ws.close();
      this.ws = null;
    }
  }

  send(data) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data));
    }
  }
}

// ============ LOCATION TRACKING ============

// Location WebSocket Manager for real-time GPS tracking
export class LocationWebSocketManager {
  constructor(role, token = null) {
    this.ws = null;
    this.role = role;
    this.token = token;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectDelay = 3000;
    this.listeners = [];
    this.locationUpdateInterval = null;
  }

  connect(onMessage, onError) {
    const wsUrl = API_BASE_URL.replace('http', 'ws');
    const url = this.token 
      ? `${wsUrl}/api/ws/location?role=${this.role}&token=${this.token}`
      : `${wsUrl}/api/ws/location?role=${this.role}`;
    
    this.ws = new WebSocket(url);

    this.ws.onopen = () => {
      console.log('✅ Location WebSocket connected');
      this.reconnectAttempts = 0;
    };

    this.ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        console.log('📍 Location update:', data);
        
        // Call all registered listeners
        this.listeners.forEach(listener => listener(data));
        
        if (onMessage) {
          onMessage(data);
        }
      } catch (error) {
        console.error('❌ Location message parse error:', error);
      }
    };

    this.ws.onerror = (error) => {
      console.error('❌ Location WebSocket error:', error);
      if (onError) {
        onError(error);
      }
    };

    this.ws.onclose = () => {
      console.log('🔌 Location WebSocket disconnected');
      
      // Attempt to reconnect
      if (this.reconnectAttempts < this.maxReconnectAttempts) {
        this.reconnectAttempts++;
        console.log(`🔄 Reconnecting location... (Attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
        setTimeout(() => {
          this.connect(onMessage, onError);
        }, this.reconnectDelay);
      }
    };
  }

  // Start sending location updates (for ambulances)
  startLocationUpdates(getLocationCallback, intervalMs = 5000) {
    if (this.role !== 'ambulance') {
      console.warn('Location updates only available for ambulances');
      return;
    }

    this.locationUpdateInterval = setInterval(() => {
      if (this.ws && this.ws.readyState === WebSocket.OPEN) {
        const location = getLocationCallback();
        if (location) {
          this.sendLocation(location);
        }
      }
    }, intervalMs);
  }

  // Stop sending location updates
  stopLocationUpdates() {
    if (this.locationUpdateInterval) {
      clearInterval(this.locationUpdateInterval);
      this.locationUpdateInterval = null;
    }
  }

  // Send location update
  sendLocation(location) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(location));
    }
  }

  addListener(callback) {
    this.listeners.push(callback);
  }

  removeListener(callback) {
    this.listeners = this.listeners.filter(l => l !== callback);
  }

  disconnect() {
    this.stopLocationUpdates();
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }
}

// Get nearest hospitals with AI recommendation
export const getNearestHospitals = async (lat, lng, limit = 10) => {
  const response = await api.get('/api/nearest-hospitals', {
    params: { lat, lng, limit }
  });
  return response.data;
};

// Get all active ambulance locations (for hospital dashboard)
export const getAmbulanceLocations = async () => {
  const response = await api.get('/api/ambulance-locations');
  return response.data;
};

// Update hospital data (beds, load)
export const updateHospitalData = async (hospitalId, availableBeds, currentLoad) => {
  const response = await api.post('/api/update-hospital-data', null, {
    params: {
      hospital_id: hospitalId,
      available_beds: availableBeds,
      current_load: currentLoad
    }
  });
  return response.data;
};

