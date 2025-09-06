import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// API endpoints
export const authAPI = {
  login: (telegram_user_id: number, username?: string, first_name?: string, last_name?: string) =>
    api.post('/auth/login/admin', {
      telegram_user_id,
      username,
      first_name,
      last_name,
    }),
  me: () => api.get('/auth/me'),
};

export const usersAPI = {
  list: (page = 1, size = 10) => api.get(`/users/?page=${page}&size=${size}`),
  get: (id: string) => api.get(`/users/${id}`),
  update: (id: string, data: any) => api.put(`/users/${id}`, data),
  delete: (id: string) => api.delete(`/users/${id}`),
};

export const botsAPI = {
  list: (page = 1, size = 10) => api.get(`/bots/all?page=${page}&size=${size}`),
  get: (id: string) => api.get(`/bots/${id}`),
  start: (id: string) => api.post(`/bots/${id}/start`),
  stop: (id: string) => api.post(`/bots/${id}/stop`),
  restart: (id: string) => api.post(`/bots/${id}/restart`),
};

export const subscriptionsAPI = {
  list: (page = 1, size = 10) => api.get(`/subscriptions/all?page=${page}&size=${size}`),
  get: (id: string) => api.get(`/subscriptions/${id}`),
  update: (id: string, data: any) => api.put(`/subscriptions/${id}`, data),
  extend: (id: string, days: number) => api.post(`/subscriptions/${id}/extend?days=${days}`),
  expiring: (days = 7) => api.get(`/subscriptions/expiring/reminders?days=${days}`),
  expired: () => api.get('/subscriptions/expired/list'),
};

export const paymentsAPI = {
  list: (page = 1, size = 10, status?: string) => {
    const params = new URLSearchParams({ page: page.toString(), size: size.toString() });
    if (status) params.append('status_filter', status);
    return api.get(`/payments/all?${params}`);
  },
  get: (id: string) => api.get(`/payments/${id}`),
  update: (id: string, data: any) => api.put(`/payments/${id}`, data),
  confirm: (id: string) => api.post(`/payments/${id}/confirm`),
  reject: (id: string, reason: string) => api.post(`/payments/${id}/reject?reason=${encodeURIComponent(reason)}`),
  pending: () => api.get('/payments/pending'),
};

export const plansAPI = {
  list: () => api.get('/subscriptions/plans'),
  create: (data: any) => api.post('/subscriptions/plans', data),
  update: (id: string, data: any) => api.put(`/subscriptions/plans/${id}`, data),
  delete: (id: string) => api.delete(`/subscriptions/plans/${id}`),
};