import React from 'react';
import { Button } from './ui/button';
import { forceReauth, clearAuthData, getStoredCredentials, storeCredentials } from '../utils/auth';
import useAuthStore from '../store/authStore';
import { authAPI } from '../lib/api';

const AuthDebug = () => {
  const { user, isAuthenticated } = useAuthStore();
  
  const handleClearAuth = () => {
    clearAuthData();
    window.location.reload();
  };

  const handleForceReauth = () => {
    forceReauth();
  };

  const checkTokens = () => {
    const accessToken = localStorage.getItem('access_token');
    const refreshToken = localStorage.getItem('refresh_token');
    const credentials = getStoredCredentials();
    
    console.log('=== AUTH DEBUG ===');
    console.log('Access Token:', accessToken ? 'Present' : 'Missing');
    console.log('Refresh Token:', refreshToken ? 'Present' : 'Missing');
    console.log('User State:', user);
    console.log('Is Authenticated:', isAuthenticated);
    console.log('Stored Credentials:', credentials ? 'Present' : 'Missing');
    console.log('==================');
  };

  const handleAutoLogin = async () => {
    try {
      // Use admin credentials for testing
      const credentials = { email: 'admin@example.com', password: 'admin123' };
      console.log('Attempting auto-login...');
      
      const response = await authAPI.login(credentials);
      const { user: userData, tokens } = response.data;
      
      useAuthStore.getState().login(userData, tokens);
      storeCredentials(credentials.email, credentials.password);
      
      console.log('Auto-login successful!');
      window.location.reload();
    } catch (error) {
      console.error('Auto-login failed:', error);
    }
  };

  return (
    <div className="fixed bottom-4 right-4 bg-white border border-gray-300 rounded-lg p-4 shadow-lg z-50">
      <h3 className="text-sm font-semibold mb-2">Auth Debug</h3>
      <div className="space-y-2">
        <Button size="sm" variant="outline" onClick={checkTokens}>
          Check Tokens
        </Button>
        <Button size="sm" variant="secondary" onClick={handleAutoLogin}>
          Auto Login
        </Button>
        <Button size="sm" variant="outline" onClick={handleClearAuth}>
          Clear Auth
        </Button>
        <Button size="sm" variant="destructive" onClick={handleForceReauth}>
          Force Re-login
        </Button>
      </div>
    </div>
  );
};

export default AuthDebug;
