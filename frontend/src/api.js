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
