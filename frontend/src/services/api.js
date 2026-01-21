import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
});

// Thêm JWT vào header tự động
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  response => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const login = async (email, password) => {
  const formData = new FormData();
  formData.append('username', email);
  formData.append('password', password);
  const response = await api.post('/auth/jwt/login', formData);
  return response.data.access_token;
};

export const scanBarcode = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  const response = await api.post('/barcodes/scan', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return response.data;
};

export const getBarcodes = async () => {
  const response = await api.get('/barcodes/list');
  return response.data.data;
};

export const deleteBarcode = async (id) => {
  await api.delete(`/barcodes/${id}`);
};

export default api;