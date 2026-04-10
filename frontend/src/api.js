// src/api.js
import axios from "axios";

const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL,
  timeout: 8000,
});

export const predictSeverity = (patient) => api.post("/predict", patient);

export const getFeatureImportance = () => api.get("/feature_importance");

export const explainPrediction = (patient) => api.post("/explain", patient);
