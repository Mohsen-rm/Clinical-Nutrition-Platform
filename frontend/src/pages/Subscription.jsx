import React from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { Link, useNavigate } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { CheckCircle, Crown, Zap, Shield } from 'lucide-react';
import { subscriptionAPI } from '../lib/api';
import { useToast } from '../components/ui/use-toast';
import { formatCurrency } from '../lib/utils';

const Subscription = () => {
  const { toast } = useToast();
  const navigate = useNavigate();

  // Fetch subscription plans
  const { data: plansResponse, isLoading: plansLoading } = useQuery({
    queryKey: ['subscription-plans'],
    queryFn: subscriptionAPI.getPlans,
  });

  const plans = plansResponse?.data?.plans || [];

  // Fetch current subscription status
  const { data: subscriptionResponse, refetch: refetchStatus } = useQuery({
    queryKey: ['subscription-status'],
    queryFn: subscriptionAPI.getStatus,
  });

  const currentSubscription = subscriptionResponse?.data?.subscription;

  // Cancel subscription mutation
  const cancelMutation = useMutation({
    mutationFn: subscriptionAPI.cancel,
    onSuccess: () => {
      toast({
        title: "Subscription cancelled",
        description: "Your subscription has been cancelled successfully.",
      });
      refetchStatus();
    },
    onError: (error) => {
      toast({
        title: "Cancellation failed",
        description: error.response?.data?.detail || "Failed to cancel subscription",
        variant: "destructive",
      });
    },
  });

  const handleCancelSubscription = () => {
    if (window.confirm('Are you sure you want to cancel your subscription?')) {
      cancelMutation.mutate({});
    }
  };

  const getPlanIcon = (planType) => {
    switch (planType) {
      case 'basic':
        return <Shield className="h-8 w-8 text-blue-500" />;
      case 'premium':
        return <Zap className="h-8 w-8 text-purple-500" />;
      case 'professional':
        return <Crown className="h-8 w-8 text-yellow-500" />;
      default:
        return <Shield className="h-8 w-8 text-gray-500" />;
    }
  };

  if (plansLoading) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-gray-200 rounded w-1/4"></div>
          <div className="grid md:grid-cols-3 gap-6">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-96 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  // If user has an active subscription, show subscription management page
  if (currentSubscription?.is_active) {
    return (
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Your Subscription
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Manage your current subscription and billing details
          </p>
        </div>

        {/* Current Subscription Details */}
        <Card className="mb-8 border-green-200 bg-green-50">
          <CardHeader>
            <CardTitle className="text-green-800 flex items-center">
              <CheckCircle className="h-6 w-6 mr-2" />
              Active Subscription
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <h3 className="font-semibold text-green-800 text-lg mb-2">
                  {currentSubscription.plan_name}
                </h3>
                <div className="space-y-2 text-sm text-green-700">
                  <p>
                    <span className="font-medium">Status:</span> {currentSubscription.status}
                  </p>
                  <p>
                    <span className="font-medium">Next billing:</span>{' '}
                    {new Date(currentSubscription.current_period_end).toLocaleDateString()}
                  </p>
                  <p>
                    <span className="font-medium">Amount:</span>{' '}
                    {formatCurrency(currentSubscription.amount / 100)}/month
                  </p>
                  <p>
                    <span className="font-medium">Days until renewal:</span>{' '}
                    {currentSubscription.days_until_renewal} days
                  </p>
                </div>
              </div>
              <div className="flex flex-col justify-center space-y-3">
                <Button 
                  variant="outline" 
                  className="w-full"
                  onClick={() => navigate('/subscription/plans')}
                >
                  Change Plan
                </Button>
                <Button 
                  variant="destructive" 
                  onClick={handleCancelSubscription}
                  disabled={cancelMutation.isPending}
                  className="w-full"
                >
                  {cancelMutation.isPending ? 'Cancelling...' : 'Cancel Subscription'}
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Subscription Benefits */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle>Your Plan Benefits</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid md:grid-cols-2 gap-4">
              {/* Find current plan features */}
              {plans.find(p => p.id === currentSubscription.plan_id)?.features?.map((feature, index) => (
                <div key={index} className="flex items-center">
                  <CheckCircle className="h-4 w-4 text-green-500 mr-2 flex-shrink-0" />
                  <span className="text-sm">{feature}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Quick Actions */}
        <div className="grid md:grid-cols-3 gap-6">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Billing History</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-gray-600 text-sm mb-4">
                View your payment history and download invoices
              </p>
              <Button variant="outline" className="w-full">
                View History
              </Button>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Update Payment</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-gray-600 text-sm mb-4">
                Update your payment method and billing information
              </p>
              <Button variant="outline" className="w-full">
                Update Payment
              </Button>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Support</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-gray-600 text-sm mb-4">
                Get help with your subscription or technical issues
              </p>
              <Button variant="outline" className="w-full">
                Contact Support
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          Choose Your Plan
        </h1>
        <p className="text-xl text-gray-600 max-w-2xl mx-auto">
          Select the perfect plan for your nutrition practice needs
        </p>
      </div>

      {/* Pricing Plans */}
      <div className="grid md:grid-cols-3 gap-8">
        {plans.length === 0 ? (
          <div className="col-span-3 text-center py-8">
            <p className="text-gray-500">No subscription plans available at the moment.</p>
          </div>
        ) : (
          plans.map((plan) => (
          <Card 
            key={plan.id} 
            className={`relative ${
              plan.plan_type === 'premium' 
                ? 'border-primary shadow-lg scale-105' 
                : ''
            }`}
          >
            {plan.plan_type === 'premium' && (
              <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
                <span className="bg-primary text-white px-3 py-1 rounded-full text-sm font-medium">
                  Most Popular
                </span>
              </div>
            )}
            
            <CardHeader className="text-center">
              <div className="flex justify-center mb-4">
                {getPlanIcon(plan.plan_type)}
              </div>
              <CardTitle className="text-2xl">{plan.name}</CardTitle>
              <CardDescription className="min-h-[3rem]">
                {plan.description}
              </CardDescription>
              <div className="text-4xl font-bold text-primary">
                {formatCurrency(plan.price)}
                <span className="text-lg text-gray-600 font-normal">/month</span>
              </div>
            </CardHeader>
            
            <CardContent>
              <ul className="space-y-3 mb-6">
                {plan.features?.map((feature, index) => (
                  <li key={index} className="flex items-center">
                    <CheckCircle className="h-4 w-4 text-green-500 mr-2 flex-shrink-0" />
                    <span className="text-sm">{feature}</span>
                  </li>
                ))}
              </ul>
              
              {currentSubscription?.plan_id === plan.id ? (
                <Button className="w-full" disabled>
                  Current Plan
                </Button>
              ) : (
                <Link 
                  to={`/checkout?plan=${plan.id}`}
                  className="block"
                >
                  <Button 
                    className="w-full" 
                    variant={plan.plan_type === 'premium' ? 'default' : 'outline'}
                  >
                    {currentSubscription?.is_active ? 'Switch Plan' : 'Get Started'}
                  </Button>
                </Link>
              )}
            </CardContent>
          </Card>
          ))
        )}
      </div>

      {/* Features Comparison */}
      <div className="mt-16">
        <h2 className="text-2xl font-bold text-center mb-8">
          Why Choose Our Platform?
        </h2>
        <div className="grid md:grid-cols-3 gap-8">
          <div className="text-center">
            <Shield className="h-12 w-12 text-primary mx-auto mb-4" />
            <h3 className="text-lg font-semibold mb-2">Secure & Compliant</h3>
            <p className="text-gray-600">
              HIPAA-compliant platform with enterprise-grade security for patient data protection.
            </p>
          </div>
          <div className="text-center">
            <Zap className="h-12 w-12 text-primary mx-auto mb-4" />
            <h3 className="text-lg font-semibold mb-2">Advanced Features</h3>
            <p className="text-gray-600">
              Disease-specific calculations, WhatsApp integration, and comprehensive analytics.
            </p>
          </div>
          <div className="text-center">
            <Crown className="h-12 w-12 text-primary mx-auto mb-4" />
            <h3 className="text-lg font-semibold mb-2">Affiliate Program</h3>
            <p className="text-gray-600">
              Earn 30% recurring commission on every referral with our generous affiliate program.
            </p>
          </div>
        </div>
      </div>

      {/* FAQ Section */}
      <div className="mt-16">
        <h2 className="text-2xl font-bold text-center mb-8">
          Frequently Asked Questions
        </h2>
        <div className="max-w-3xl mx-auto space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Can I change my plan anytime?</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-gray-600">
                Yes, you can upgrade or downgrade your plan at any time. Changes will be prorated and reflected in your next billing cycle.
              </p>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">What payment methods do you accept?</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-gray-600">
                We accept all major credit cards (Visa, MasterCard, American Express) through our secure Stripe payment processor.
              </p>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Is there a free trial?</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-gray-600">
                We offer a 14-day free trial for all new users. No credit card required to get started.
              </p>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default Subscription;
