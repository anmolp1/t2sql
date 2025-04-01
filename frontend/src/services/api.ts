import axios, { AxiosError } from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests if available
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  console.log('API Request:', {
    url: config.url,
    method: config.method,
    hasToken: !!token,
    headers: config.headers
  });
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
}, (error) => {
  console.error('Request interceptor error:', error);
  return Promise.reject(error);
});

// Add response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    console.log('API Response:', {
      url: response.config.url,
      method: response.config.method,
      status: response.status,
      data: response.data
    });
    return response;
  },
  async (error: AxiosError) => {
    console.error('API Error:', {
      url: error.config?.url,
      method: error.config?.method,
      requestData: error.config?.data,
      status: error.response?.status,
      statusText: error.response?.statusText,
      responseData: error.response?.data,
      headers: error.config?.headers
    });

    if (error.response?.status === 401) {
      // Clear token and redirect to login
      localStorage.removeItem('token');
      window.location.href = '/login';
      return Promise.reject(error);
    }

    return Promise.reject(error);
  }
);

// Auth API
export const login = (email: string, password: string) => {
  const formData = new URLSearchParams();
  formData.append('username', email);
  formData.append('password', password);
  
  return api.post('/auth/login', formData, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
  });
};

export const register = (email: string, password: string, fullName: string) =>
  api.post('/auth/register', { email, password, full_name: fullName });

// Database Connections API
export const createDatabaseConnection = (data: any) =>
  api.post('/databases/', data);

export const getDatabaseConnections = () =>
  api.get('/databases/');

export const getDatabaseConnection = (id: number) =>
  api.get(`/databases/${id}/`);

export const updateDatabaseConnection = (id: number, data: any) =>
  api.put(`/databases/${id}/`, data);

export const deleteDatabaseConnection = (id: number) =>
  api.delete(`/databases/${id}/`);

export const extractDatabaseMetadata = (id: number) =>
  api.post(`/databases/${id}/metadata`);

// Query API
export const generateSQLQuery = (connectionId: number, question: string) =>
  api.post(`/query/${connectionId}/generate`, { question });

export default api; 