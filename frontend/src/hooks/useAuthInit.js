import { useEffect } from 'react';
import useAuthStore from '../store/authStore';
import { authAPI } from '../lib/api';

const useAuthInit = () => {
  const { user, setUser, setLoading, isAuthenticated } = useAuthStore();

  useEffect(() => {
    const initializeAuth = async () => {
      const token = localStorage.getItem('access_token');
      
      if (token && !user) {
        setLoading(true);
        try {
          const response = await authAPI.getProfile();
          setUser(response.data.user);
        } catch (error) {
          console.error('Failed to initialize auth:', error);
          // Clear invalid tokens
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
        } finally {
          setLoading(false);
        }
      }
    };

    initializeAuth();
  }, [user, setUser, setLoading]);

  return { isAuthenticated, user };
};

export default useAuthInit;
