import axios from 'axios';
import { clearAuthData } from '../utils/auth';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Create axios instance
const api = axios.create({
  baseURL: `${API_URL}/api`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // Only try to refresh token for 401 errors and avoid infinite loops
    if (error.response?.status === 401 && !originalRequest._retry && !originalRequest.url?.includes('/token/refresh/')) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (refreshToken) {
          console.log('Attempting token refresh...');
          const refreshResponse = await axios.post(`${API_URL}/api/auth/token/refresh/`, {
            refresh: refreshToken,
          });

          const { access } = refreshResponse.data;
          localStorage.setItem('access_token', access);
          console.log('Token refreshed successfully');

          // Update the authorization header for the original request
          originalRequest.headers.Authorization = `Bearer ${access}`;
          
          // Retry the original request
          return api(originalRequest);
        } else {
          console.log('No refresh token available');
          throw new Error('No refresh token');
        }
      } catch (refreshError) {
        console.error('Token refresh failed:', refreshError);
        // Clear auth data and redirect to login
        clearAuthData();
        
        // Only redirect if we're not already on the login page
        if (!window.location.pathname.includes('/login')) {
          window.location.href = '/login';
        }
        
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  login: (credentials) => api.post('/auth/login/', credentials),
  register: (userData) => api.post('/auth/register/', userData),
  logout: (refreshToken) => api.post('/auth/logout/', { refresh_token: refreshToken }),
  getProfile: () => api.get('/auth/profile/'),
  updateProfile: (data) => api.put('/auth/profile/', data),
  changePassword: (data) => api.post('/auth/change-password/', data),
  checkReferralCode: (code) => api.get(`/auth/referral/${code}/`),
};

// Subscription API
export const subscriptionAPI = {
  getPlans: () => api.get('/subscriptions/plans/'),
  createSubscription: (data) => api.post('/subscriptions/create/', data),
  getStatus: () => api.get('/subscriptions/status/'),
  cancel: (data) => api.post('/subscriptions/cancel/', data),
  createPaymentIntent: (data) => api.post('/subscriptions/payment-intent/', data),
};

// Affiliate API
export const affiliateAPI = {
  getStats: () => api.get('/affiliates/stats/'),
  getCommissions: (params) => api.get('/affiliates/commissions/', { params }),
  getReferrals: () => api.get('/affiliates/referrals/'),
  getPayoutRequests: () => api.get('/affiliates/payouts/'),
  createPayoutRequest: (data) => api.post('/affiliates/payouts/', data),
  generateLink: () => api.post('/affiliates/generate-link/'),
  getDashboard: () => api.get('/affiliates/dashboard/'),
};

// Nutrition API
export const nutritionAPI = {
  getDiseases: () => api.get('/nutrition/diseases/'),
  getPlans: () => api.get('/nutrition/plans/'),
  createPlan: (data) => api.post('/nutrition/plans/', data),
  getPlan: (id) => api.get(`/nutrition/plans/${id}/`),
  updatePlan: (id, data) => api.put(`/nutrition/plans/${id}/`, data),
  calculateCalories: (data) => api.post('/nutrition/calculate/', data),
  getWhatsAppMessages: () => api.get('/nutrition/whatsapp/'),
  sendWhatsAppMessage: (data) => api.post('/nutrition/whatsapp/', data),
  getDemo: () => api.get('/nutrition/demo/'),
};

export default api;
