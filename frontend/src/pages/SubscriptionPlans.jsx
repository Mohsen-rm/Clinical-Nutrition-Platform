import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link, useNavigate } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { CheckCircle, Crown, Zap, Shield, ArrowLeft } from 'lucide-react';
import { subscriptionAPI } from '../lib/api';
import { formatCurrency } from '../lib/utils';

const SubscriptionPlans = () => {
  const navigate = useNavigate();

  // Fetch subscription plans
  const { data: plansResponse, isLoading: plansLoading } = useQuery({
    queryKey: ['subscription-plans'],
    queryFn: subscriptionAPI.getPlans,
  });

  const plans = plansResponse?.data?.plans || [];

  // Fetch current subscription status
  const { data: subscriptionResponse } = useQuery({
    queryKey: ['subscription-status'],
    queryFn: subscriptionAPI.getStatus,
  });

  const currentSubscription = subscriptionResponse?.data?.subscription;

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

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Back Button */}
      <div className="mb-6">
        <Button 
          variant="ghost" 
          onClick={() => navigate('/subscription')}
          className="flex items-center"
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Subscription
        </Button>
      </div>

      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          {currentSubscription?.is_active ? 'Change Your Plan' : 'Choose Your Plan'}
        </h1>
        <p className="text-xl text-gray-600 max-w-2xl mx-auto">
          {currentSubscription?.is_active 
            ? 'Upgrade or downgrade your subscription plan'
            : 'Select the perfect plan for your nutrition practice needs'
          }
        </p>
      </div>

      {/* Current Plan Indicator */}
      {currentSubscription?.is_active && (
        <div className="text-center mb-8">
          <div className="inline-flex items-center px-4 py-2 bg-green-100 text-green-800 rounded-full">
            <CheckCircle className="h-4 w-4 mr-2" />
            Currently on {currentSubscription.plan_name}
          </div>
        </div>
      )}

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
            } ${
              currentSubscription?.plan_id === plan.id
                ? 'border-green-500 bg-green-50'
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

            {currentSubscription?.plan_id === plan.id && (
              <div className="absolute -top-3 right-4">
                <span className="bg-green-500 text-white px-3 py-1 rounded-full text-sm font-medium">
                  Current Plan
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
                    {currentSubscription?.is_active ? 'Switch to This Plan' : 'Get Started'}
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
    </div>
  );
};

export default SubscriptionPlans;
