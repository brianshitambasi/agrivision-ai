import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_URL,
  timeout: 30000,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const register = (data) => api.post('/auth/register', data);
export const login = (data) => api.post('/auth/login', data);
export const getMe = () => api.get('/auth/me');

export const predictImage = (file) => {
  const form = new FormData();
  form.append('file', file);
  return api.post('/ai/predict', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
};

export const getDiagnoses = () => api.get('/diagnoses');
export const deleteDiagnosis = (id) => api.delete(`/diagnoses/${id}`);

export default api;
