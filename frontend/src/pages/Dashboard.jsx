import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Users, CreditCard, TrendingUp, Activity, Plus, Eye } from 'lucide-react';
import useAuthStore from '../store/authStore';
import { subscriptionAPI, affiliateAPI, nutritionAPI } from '../lib/api';

const Dashboard = () => {
  const { user, isDoctor, isAuthenticated } = useAuthStore();

  // Fetch subscription status
  const { data: subscriptionResponse } = useQuery({
    queryKey: ['subscription-status'],
    queryFn: subscriptionAPI.getStatus,
    enabled: isAuthenticated && !!user,
  });

  // Fetch affiliate stats for doctors
  const { data: affiliateStatsResponse } = useQuery({
    queryKey: ['affiliate-stats'],
    queryFn: affiliateAPI.getStats,
    enabled: isAuthenticated && isDoctor() && !!user,
  });

  // Fetch nutrition plans
  const { data: nutritionPlansResponse } = useQuery({
    queryKey: ['nutrition-plans'],
    queryFn: nutritionAPI.getPlans,
    enabled: isAuthenticated && !!user,
  });

  const subscriptionStatus = subscriptionResponse?.data?.subscription;
  const affiliateStats = affiliateStatsResponse?.data;
  const nutritionPlans = nutritionPlansResponse?.data?.plans || [];

  const DoctorDashboard = () => (
    <div className="space-y-6">
      {/* Subscription Status */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <CreditCard className="h-5 w-5" />
            Subscription Status
          </CardTitle>
        </CardHeader>
        <CardContent>
          {subscriptionStatus?.is_active ? (
            <div className="flex items-center justify-between">
              <div>
                <p className="text-green-600 font-semibold">Active Subscription</p>
                <p className="text-sm text-gray-600">
                  Plan: {subscriptionStatus.plan_name}
                </p>
                <p className="text-sm text-gray-600">
                  Next billing: {new Date(subscriptionStatus.current_period_end).toLocaleDateString()}
                </p>
              </div>
              <Link to="/subscription">
                <Button variant="outline">Manage</Button>
              </Link>
            </div>
          ) : (
            <div className="flex items-center justify-between">
              <div>
                <p className="text-red-600 font-semibold">No Active Subscription</p>
                <p className="text-sm text-gray-600">
                  Subscribe to access all features
                </p>
              </div>
              <Link to="/subscription">
                <Button>Subscribe Now</Button>
              </Link>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Stats Grid */}
      <div className="grid md:grid-cols-3 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Patients</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {nutritionPlans?.length || 0}
            </div>
            <p className="text-xs text-muted-foreground">
              Active nutrition plans
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Referral Earnings</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              ${affiliateStats?.total_earnings?.toFixed(2) || '0.00'}
            </div>
            <p className="text-xs text-muted-foreground">
              Total commission earned
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Referrals</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {affiliateStats?.total_referrals || 0}
            </div>
            <p className="text-xs text-muted-foreground">
              People referred
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Quick Actions</CardTitle>
          <CardDescription>
            Common tasks and features
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-2 gap-4">
            <Link to="/nutrition">
              <Button className="w-full justify-start" variant="outline">
                <Plus className="mr-2 h-4 w-4" />
                Create Nutrition Plan
              </Button>
            </Link>
            <Link to="/affiliate">
              <Button className="w-full justify-start" variant="outline">
                <TrendingUp className="mr-2 h-4 w-4" />
                View Affiliate Dashboard
              </Button>
            </Link>
          </div>
        </CardContent>
      </Card>
    </div>
  );

  const PatientDashboard = () => (
    <div className="space-y-6">
      {/* Welcome Card */}
      <Card>
        <CardHeader>
          <CardTitle>Welcome, {user?.first_name}!</CardTitle>
          <CardDescription>
            Track your nutrition journey and health goals
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-4">
            <Activity className="h-8 w-8 text-primary" />
            <div>
              <p className="font-medium">Your Health Dashboard</p>
              <p className="text-sm text-gray-600">
                Monitor your progress and nutrition plans
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Nutrition Plans */}
      <Card>
        <CardHeader>
          <CardTitle>My Nutrition Plans</CardTitle>
          <CardDescription>
            View and manage your personalized nutrition plans
          </CardDescription>
        </CardHeader>
        <CardContent>
          {nutritionPlans?.length > 0 ? (
            <div className="space-y-4">
              {nutritionPlans.slice(0, 3).map((plan) => (
                <div key={plan.id} className="flex items-center justify-between p-4 border rounded-lg">
                  <div>
                    <h4 className="font-medium">{plan.name || 'Nutrition Plan'}</h4>
                    <p className="text-sm text-gray-600">
                      Created: {new Date(plan.created_at).toLocaleDateString()}
                    </p>
                  </div>
                  <Link to={`/nutrition`}>
                    <Button size="sm" variant="outline">
                      <Eye className="mr-2 h-4 w-4" />
                      View
                    </Button>
                  </Link>
                </div>
              ))}
              <Link to="/nutrition">
                <Button className="w-full" variant="outline">
                  View All Plans
                </Button>
              </Link>
            </div>
          ) : (
            <div className="text-center py-8">
              <Activity className="mx-auto h-12 w-12 text-gray-400 mb-4" />
              <p className="text-gray-600 mb-4">No nutrition plans yet</p>
              <Link to="/nutrition">
                <Button>
                  <Plus className="mr-2 h-4 w-4" />
                  Get Started
                </Button>
              </Link>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">
          Dashboard
        </h1>
        <p className="text-gray-600 mt-2">
          {isDoctor() ? 'Manage your practice and track your success' : 'Track your health and nutrition journey'}
        </p>
      </div>

      {isDoctor() ? <DoctorDashboard /> : <PatientDashboard />}
    </div>
  );
};

export default Dashboard;
