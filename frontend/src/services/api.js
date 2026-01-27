import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
});

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

export const register = async (email, password, fullName = '') => {
  const response = await api.post('/auth/jwt/register', {
    email,
    password,
    full_name: fullName,
  });
  return response.data;
};

export const scanBarcode = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  const response = await api.post('/barcodes/scan', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return response.data;
};

export const getBarcodes = async (limit = 10, offset = 0) => {
  const response = await api.get(`/barcodes/list?limit=${limit}&offset=${offset}`);
  return { data: response.data.data, total: response.data.count };
};

export const deleteBarcode = async (id) => {
  await api.delete(`/barcodes/${id}`);
};

export const getUserInfo = async () => {
  const response = await api.get('/users/me');
  return response.data;
};

export const updateUser = async (data) => {
  await api.patch('/users/me', data);
};

export const getUsers = async () => {
  const response = await api.get('/users');
  return response.data;
};

export const deleteUser = async (id) => {
  await api.delete(`/users/${id}`);
};

export default api;
