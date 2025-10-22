import { create } from 'zustand';
import { persist } from 'zustand/middleware';

const useAuthStore = create(
  persist(
    (set, get) => ({
      user: null,
      isAuthenticated: false,
      isLoading: false,
      isInitialized: false,

      setUser: (user) => set({ 
        user, 
        isAuthenticated: !!user,
        isInitialized: true 
      }),
      
      setLoading: (isLoading) => set({ isLoading }),

      setInitialized: (isInitialized) => set({ isInitialized }),

      login: (userData, tokens) => {
        localStorage.setItem('access_token', tokens.access);
        localStorage.setItem('refresh_token', tokens.refresh);
        set({ 
          user: userData, 
          isAuthenticated: true,
          isLoading: false,
          isInitialized: true
        });
      },

      logout: () => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        set({ 
          user: null, 
          isAuthenticated: false,
          isLoading: false,
          isInitialized: true
        });
      },

      updateUser: (userData) => set({ user: userData }),

      // Check if token exists and is potentially valid
      hasValidToken: () => {
        const token = localStorage.getItem('access_token');
        const refreshToken = localStorage.getItem('refresh_token');
        return !!(token && refreshToken);
      },

      // Check if user has active subscription
      hasActiveSubscription: () => {
        const { user } = get();
        return user?.subscription?.is_active || false;
      },

      // Check if user is doctor
      isDoctor: () => {
        const { user } = get();
        return user?.user_type === 'doctor';
      },

      // Check if user is patient
      isPatient: () => {
        const { user } = get();
        return user?.user_type === 'patient';
      },

      // Check if user is admin
      isAdmin: () => {
        const { user } = get();
        return user?.user_type === 'admin' || user?.is_staff || user?.is_superuser;
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        isAuthenticated: state.isAuthenticated,
        isInitialized: state.isInitialized,
      }),
    }
  )
);

export default useAuthStore;
