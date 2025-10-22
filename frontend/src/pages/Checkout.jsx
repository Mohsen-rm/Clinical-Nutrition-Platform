import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation } from '@tanstack/react-query';
import { loadStripe } from '@stripe/stripe-js';
import { Elements, CardElement, useStripe, useElements } from '@stripe/react-stripe-js';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { subscriptionAPI } from '../lib/api';
import { useToast } from '../components/ui/use-toast';
import { formatCurrency } from '../lib/utils';
import { CreditCard, Shield, CheckCircle } from 'lucide-react';

const stripePromise = loadStripe(process.env.REACT_APP_STRIPE_PUBLISHABLE_KEY);

const CheckoutForm = ({ plan }) => {
  const stripe = useStripe();
  const elements = useElements();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [isProcessing, setIsProcessing] = useState(false);

  // Create subscription
  const subscriptionMutation = useMutation({
    mutationFn: subscriptionAPI.createSubscription,
    onSuccess: () => {
      toast({
        title: "Subscription created successfully!",
        description: "Welcome to your new plan. Redirecting to dashboard...",
      });
      setTimeout(() => navigate('/dashboard'), 2000);
    },
    onError: (error) => {
      toast({
        title: "Subscription failed",
        description: error.response?.data?.detail || "Failed to create subscription",
        variant: "destructive",
      });
      setIsProcessing(false);
    },
  });

  const handleSubmit = async (event) => {
    event.preventDefault();
    
    if (!stripe || !elements) {
      return;
    }

    setIsProcessing(true);

    try {
      const cardElement = elements.getElement(CardElement);

      // Create payment method
      const { error: paymentMethodError, paymentMethod } = await stripe.createPaymentMethod({
        type: 'card',
        card: cardElement,
      });

      if (paymentMethodError) {
        toast({
          title: "Payment method creation failed",
          description: paymentMethodError.message,
          variant: "destructive",
        });
        setIsProcessing(false);
        return;
      }

      // Create subscription directly with payment method
      subscriptionMutation.mutate({
        plan_id: plan.id,
        payment_method_id: paymentMethod.id,
      });

    } catch (error) {
      toast({
        title: "Payment processing failed",
        description: "Please try again or contact support",
        variant: "destructive",
      });
      setIsProcessing(false);
    }
  };

  return (
    <div className="grid md:grid-cols-2 gap-8">
      {/* Plan Summary */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <CheckCircle className="h-5 w-5 text-green-500" />
            Order Summary
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="font-medium">{plan.name}</span>
              <span className="font-bold">{formatCurrency(plan.price)}/month</span>
            </div>
            
            <div className="border-t pt-4">
              <h4 className="font-medium mb-2">Included Features:</h4>
              <ul className="space-y-1 text-sm text-gray-600">
                {plan.features?.map((feature, index) => (
                  <li key={index} className="flex items-center">
                    <CheckCircle className="h-3 w-3 text-green-500 mr-2" />
                    {feature}
                  </li>
                ))}
              </ul>
            </div>

            <div className="border-t pt-4">
              <div className="flex justify-between items-center text-lg font-bold">
                <span>Total</span>
                <span>{formatCurrency(plan.price)}/month</span>
              </div>
              <p className="text-sm text-gray-600 mt-1">
                Billed monthly • Cancel anytime
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Payment Form */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <CreditCard className="h-5 w-5" />
            Payment Information
          </CardTitle>
          <CardDescription>
            Enter your payment details to complete your subscription
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Card Information
              </label>
              <div className="p-3 border rounded-md">
                <CardElement
                  options={{
                    style: {
                      base: {
                        fontSize: '16px',
                        color: '#424770',
                        '::placeholder': {
                          color: '#aab7c4',
                        },
                      },
                    },
                  }}
                />
              </div>
            </div>

            <div className="flex items-center gap-2 text-sm text-gray-600">
              <Shield className="h-4 w-4" />
              <span>Your payment information is secure and encrypted</span>
            </div>

            <Button
              type="submit"
              className="w-full"
              disabled={!stripe || isProcessing || subscriptionMutation.isPending}
            >
              {isProcessing || subscriptionMutation.isPending ? (
                'Processing...'
              ) : (
                `Subscribe for ${formatCurrency(plan.price)}/month`
              )}
            </Button>

            <p className="text-xs text-gray-500 text-center">
              By subscribing, you agree to our Terms of Service and Privacy Policy.
              You can cancel your subscription at any time.
            </p>
          </form>
        </CardContent>
      </Card>
    </div>
  );
};

const Checkout = () => {
  const [searchParams] = useSearchParams();
  const planId = searchParams.get('plan');
  const navigate = useNavigate();

  // Fetch plan details
  const { data: plansResponse, isLoading } = useQuery({
    queryKey: ['subscription-plans'],
    queryFn: subscriptionAPI.getPlans,
  });

  const plans = plansResponse?.data?.plans || [];
  const plan = plans.find(p => p.id.toString() === planId);

  useEffect(() => {
    if (!planId) {
      navigate('/subscription');
    }
  }, [planId, navigate]);

  if (isLoading) {
    return (
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-gray-200 rounded w-1/4"></div>
          <div className="h-96 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  if (!plan) {
    return (
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Card>
          <CardContent className="text-center py-8">
            <h2 className="text-xl font-semibold mb-2">Plan not found</h2>
            <p className="text-gray-600 mb-4">
              The subscription plan you're looking for doesn't exist.
            </p>
            <Button onClick={() => navigate('/subscription')}>
              View Available Plans
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Complete Your Subscription
        </h1>
        <p className="text-gray-600">
          You're subscribing to the {plan.name} plan
        </p>
      </div>

      <Elements stripe={stripePromise}>
        <CheckoutForm plan={plan} />
      </Elements>
    </div>
  );
};

export default Checkout;
