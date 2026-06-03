import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
});

export const getDashboardSummary = () => api.get('/dashboard/summary');
export const getAnomalyTrend = () => api.get('/dashboard/anomaly-trend');
export const getCompressorDetail = (id) => api.get(`/compressor/${id}`);
export const getCompressorHealthHistory = (id) => api.get(`/compressor/${id}/health-history`);
export const getExplanation = (id) => api.get(`/insights/explain/${id}`);
export const getHealthScore = (id) => api.get(`/insights/health-score/${id}`);
export const getMaintenanceRecommendations = () => api.get('/insights/maintenance-recommendations');
export const predictAnomaly = (data) => api.post('/anomaly/predict', data);
export const batchPredict = (data) => api.post('/anomaly/batch', data);

export default api;
