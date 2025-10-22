import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Elements } from '@stripe/react-stripe-js';
import { loadStripe } from '@stripe/stripe-js';

// Components
import Layout from './components/Layout';
import ProtectedRoute from './components/ProtectedRoute';
import AuthRedirect from './components/AuthRedirect';

// Pages
import Home from './pages/Home';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import Subscription from './pages/Subscription';
import SubscriptionPlans from './pages/SubscriptionPlans';
import Checkout from './pages/Checkout';
import Affiliate from './pages/Affiliate';
import Profile from './pages/Profile';
import NutritionPlan from './pages/NutritionPlan';
import NutritionPlanDetails from './pages/NutritionPlanDetails';
import PublicNutritionPlans from './pages/PublicNutritionPlans';

// Utils
import { Toaster } from './components/ui/toaster';
import useAuthStore from './store/authStore';
import { authAPI } from './lib/api';

// Initialize Stripe
const stripePromise = loadStripe(process.env.REACT_APP_STRIPE_PUBLISHABLE_KEY);

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

function App() {
  const { user, setUser, setLoading, isInitialized, setInitialized } = useAuthStore();

  useEffect(() => {
    const initializeAuth = async () => {
      const token = localStorage.getItem('access_token');
      
      if (token && !isInitialized) {
        setLoading(true);
        try {
          const response = await authAPI.getProfile();
          setUser(response.data.user);
        } catch (error) {
          console.error('Failed to initialize auth:', error);
          // Clear invalid tokens and auth state
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          setUser(null);
        } finally {
          setLoading(false);
          setInitialized(true);
        }
      } else if (!token && !isInitialized) {
        // No token, clear any existing user state
        setUser(null);
        setInitialized(true);
      }
    };

    initializeAuth();
  }, [setUser, setLoading, isInitialized, setInitialized]);

  return (
    <QueryClientProvider client={queryClient}>
      <Elements stripe={stripePromise}>
        <Router>
          <div className="min-h-screen bg-background">
            <Routes>
              {/* Public routes */}
              <Route path="/" element={<Layout><Home /></Layout>} />
              <Route path="/plans" element={<Layout><PublicNutritionPlans /></Layout>} />
              <Route path="/login" element={
                <AuthRedirect>
                  <Layout><Login /></Layout>
                </AuthRedirect>
              } />
              <Route path="/register" element={
                <AuthRedirect>
                  <Layout><Register /></Layout>
                </AuthRedirect>
              } />
              
              {/* Protected routes */}
              <Route path="/dashboard" element={
                <ProtectedRoute>
                  <Layout><Dashboard /></Layout>
                </ProtectedRoute>
              } />
              <Route path="/subscription" element={
                <ProtectedRoute>
                  <Layout><Subscription /></Layout>
                </ProtectedRoute>
              } />
              <Route path="/subscription/plans" element={
                <ProtectedRoute>
                  <Layout><SubscriptionPlans /></Layout>
                </ProtectedRoute>
              } />
              <Route path="/checkout" element={
                <ProtectedRoute>
                  <Layout><Checkout /></Layout>
                </ProtectedRoute>
              } />
              <Route path="/affiliate" element={
                <ProtectedRoute>
                  <Layout><Affiliate /></Layout>
                </ProtectedRoute>
              } />
              <Route path="/profile" element={
                <ProtectedRoute>
                  <Layout><Profile /></Layout>
                </ProtectedRoute>
              } />
              <Route path="/nutrition" element={
                <ProtectedRoute>
                  <Layout><NutritionPlan /></Layout>
                </ProtectedRoute>
              } />
              <Route path="/nutrition/plan/:id" element={
                <ProtectedRoute>
                  <Layout><NutritionPlanDetails /></Layout>
                </ProtectedRoute>
              } />
            </Routes>
            <Toaster />
          </div>
        </Router>
      </Elements>
    </QueryClientProvider>
  );
}

export default App;
