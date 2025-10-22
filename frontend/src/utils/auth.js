import useAuthStore from '../store/authStore';

export const clearAuthData = () => {
  // Clear localStorage
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  
  // Clear Zustand state
  useAuthStore.getState().logout();
  
  // Clear any persisted data
  localStorage.removeItem('auth-storage');
};

export const getStoredCredentials = () => {
  try {
    const stored = localStorage.getItem('temp_credentials');
    return stored ? JSON.parse(stored) : null;
  } catch {
    return null;
  }
};

export const storeCredentials = (email, password) => {
  // Store temporarily for auto re-login (remove in production)
  localStorage.setItem('temp_credentials', JSON.stringify({ email, password }));
};

export const clearStoredCredentials = () => {
  localStorage.removeItem('temp_credentials');
};

export const forceReauth = () => {
  clearAuthData();
  window.location.href = '/login';
};

export const isTokenExpired = (token) => {
  if (!token) return true;
  
  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    const currentTime = Date.now() / 1000;
    return payload.exp < currentTime;
  } catch (error) {
    return true;
  }
};
