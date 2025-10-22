import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { 
  Heart, 
  Activity, 
  Target, 
  Calculator,
  CreditCard,
  Eye,
  Users,
  TrendingUp,
  Award,
  CheckCircle
} from 'lucide-react';
import { nutritionAPI, subscriptionAPI } from '../lib/api';
import useAuthStore from '../store/authStore';
import { useToast } from '../components/ui/use-toast';

const PublicNutritionPlans = () => {
  const navigate = useNavigate();
  const { user, isAuthenticated } = useAuthStore();
  const { toast } = useToast();
  const [selectedCategory, setSelectedCategory] = useState('all');

  // Fetch subscription plans
  const { data: subscriptionPlansResponse } = useQuery({
    queryKey: ['subscription-plans'],
    queryFn: subscriptionAPI.getPlans,
  });

  // Fetch sample nutrition plans (for demo)
  const { data: samplePlansResponse } = useQuery({
    queryKey: ['nutrition-demo'],
    queryFn: nutritionAPI.getDemo,
  });

  const subscriptionPlans = subscriptionPlansResponse?.data?.plans || [];
  const demoData = samplePlansResponse?.data;

  // Sample nutrition plan templates
  const nutritionPlanTemplates = [
    {
      id: 1,
      name: "Weight Loss Plan",
      category: "weight_loss",
      description: "Designed for healthy weight loss with balanced nutrition",
      targetCalories: "1500-1800",
      duration: "12 weeks",
      features: [
        "Calorie deficit calculation",
        "High protein meals",
        "Portion control guidance",
        "Weekly progress tracking"
      ],
      suitableFor: ["Overweight individuals", "Sedentary lifestyle", "Beginners"],
      diseases: ["Diabetes Type 2", "Hypertension"],
      price: "Included in subscription",
      popularity: 95
    },
    {
      id: 2,
      name: "Muscle Gain Plan",
      category: "muscle_gain",
      description: "Optimized for muscle building and strength training",
      targetCalories: "2200-2800",
      duration: "16 weeks",
      features: [
        "High protein intake",
        "Pre/post workout meals",
        "Supplement recommendations",
        "Strength training support"
      ],
      suitableFor: ["Athletes", "Active individuals", "Gym enthusiasts"],
      diseases: [],
      price: "Included in subscription",
      popularity: 88
    },
    {
      id: 3,
      name: "Heart Healthy Plan",
      category: "medical",
      description: "Specialized plan for cardiovascular health",
      targetCalories: "1800-2200",
      duration: "Ongoing",
      features: [
        "Low sodium meals",
        "Omega-3 rich foods",
        "Fiber optimization",
        "Cholesterol management"
      ],
      suitableFor: ["Heart patients", "High cholesterol", "Hypertension"],
      diseases: ["Cardiovascular Disease", "Hypertension"],
      price: "Professional plan required",
      popularity: 92
    },
    {
      id: 4,
      name: "Diabetes Management",
      category: "medical",
      description: "Comprehensive plan for diabetes control",
      targetCalories: "1600-2000",
      duration: "Ongoing",
      features: [
        "Carb counting system",
        "Blood sugar optimization",
        "Meal timing guidance",
        "Glycemic index focus"
      ],
      suitableFor: ["Type 1 & 2 diabetes", "Pre-diabetes", "Insulin users"],
      diseases: ["Diabetes Type 2"],
      price: "Professional plan required",
      popularity: 90
    },
    {
      id: 5,
      name: "Maintenance Plan",
      category: "maintenance",
      description: "Balanced nutrition for weight maintenance",
      targetCalories: "2000-2400",
      duration: "Ongoing",
      features: [
        "Balanced macronutrients",
        "Flexible meal options",
        "Lifestyle integration",
        "Long-term sustainability"
      ],
      suitableFor: ["Healthy weight individuals", "Active lifestyle", "Long-term health"],
      diseases: [],
      price: "Included in subscription",
      popularity: 85
    }
  ];

  const categories = [
    { id: 'all', name: 'All Plans', icon: Users },
    { id: 'weight_loss', name: 'Weight Loss', icon: TrendingUp },
    { id: 'muscle_gain', name: 'Muscle Gain', icon: Activity },
    { id: 'medical', name: 'Medical', icon: Heart },
    { id: 'maintenance', name: 'Maintenance', icon: Target }
  ];

  const filteredPlans = selectedCategory === 'all' 
    ? nutritionPlanTemplates 
    : nutritionPlanTemplates.filter(plan => plan.category === selectedCategory);

  const handleSubscribe = (planType = 'basic') => {
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }
    navigate(`/subscription?plan=${planType}`);
  };

  const handleViewSample = (planId) => {
    toast({
      title: "Sample Plan",
      description: "Subscribe to access full plan details and personalization",
    });
  };

  const getPlanRequirement = (plan) => {
    if (plan.price.includes('Professional')) {
      return { type: 'professional', color: 'bg-purple-100 text-purple-800' };
    }
    return { type: 'basic', color: 'bg-green-100 text-green-800' };
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          Professional Nutrition Plans
        </h1>
        <p className="text-xl text-gray-600 max-w-3xl mx-auto">
          Discover scientifically-designed nutrition plans tailored for your health goals. 
          Get personalized recommendations from certified nutritionists.
        </p>
      </div>

      {/* Subscription Plans Overview */}
      <div className="mb-12">
        <h2 className="text-2xl font-bold text-gray-900 mb-6 text-center">Choose Your Plan</h2>
        <div className="grid md:grid-cols-3 gap-6">
          {subscriptionPlans.map((plan) => (
            <Card key={plan.id} className="relative hover:shadow-lg transition-shadow">
              {plan.name === 'Professional Plan' && (
                <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
                  <Badge className="bg-purple-600 text-white">
                    <Award className="h-3 w-3 mr-1" />
                    Most Popular
                  </Badge>
                </div>
              )}
              <CardHeader className="text-center">
                <CardTitle className="text-xl">{plan.name}</CardTitle>
                <div className="text-3xl font-bold text-primary">
                  ${plan.price}<span className="text-sm font-normal text-gray-600">/month</span>
                </div>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2 mb-6">
                  {plan.features?.map((feature, index) => (
                    <li key={index} className="flex items-center text-sm">
                      <CheckCircle className="h-4 w-4 text-green-500 mr-2 flex-shrink-0" />
                      {feature}
                    </li>
                  ))}
                </ul>
                <Button 
                  className="w-full" 
                  onClick={() => handleSubscribe(plan.name.toLowerCase().replace(' plan', ''))}
                  variant={plan.name === 'Professional Plan' ? 'default' : 'outline'}
                >
                  <CreditCard className="h-4 w-4 mr-2" />
                  Subscribe Now
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>

      {/* Category Filter */}
      <div className="mb-8">
        <div className="flex flex-wrap justify-center gap-2">
          {categories.map((category) => {
            const Icon = category.icon;
            return (
              <Button
                key={category.id}
                variant={selectedCategory === category.id ? 'default' : 'outline'}
                size="sm"
                onClick={() => setSelectedCategory(category.id)}
                className="flex items-center gap-2"
              >
                <Icon className="h-4 w-4" />
                {category.name}
              </Button>
            );
          })}
        </div>
      </div>

      {/* Nutrition Plans Grid */}
      <div className="grid lg:grid-cols-2 gap-8">
        {filteredPlans.map((plan) => {
          const requirement = getPlanRequirement(plan);
          return (
            <Card key={plan.id} className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <CardTitle className="text-xl mb-2">{plan.name}</CardTitle>
                    <CardDescription className="text-base">
                      {plan.description}
                    </CardDescription>
                  </div>
                  <div className="text-right">
                    <Badge className={requirement.color}>
                      {requirement.type === 'professional' ? 'Pro' : 'Basic'}
                    </Badge>
                    <div className="text-sm text-gray-500 mt-1">
                      {plan.popularity}% success rate
                    </div>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Plan Stats */}
                <div className="grid grid-cols-2 gap-4">
                  <div className="text-center p-3 bg-blue-50 rounded-lg">
                    <Calculator className="h-5 w-5 mx-auto text-blue-600 mb-1" />
                    <div className="text-sm font-medium text-blue-800">Target Calories</div>
                    <div className="text-lg font-bold text-blue-600">{plan.targetCalories}</div>
                  </div>
                  <div className="text-center p-3 bg-green-50 rounded-lg">
                    <Target className="h-5 w-5 mx-auto text-green-600 mb-1" />
                    <div className="text-sm font-medium text-green-800">Duration</div>
                    <div className="text-lg font-bold text-green-600">{plan.duration}</div>
                  </div>
                </div>

                {/* Features */}
                <div>
                  <h4 className="font-medium text-gray-900 mb-2">Key Features:</h4>
                  <ul className="space-y-1">
                    {plan.features.map((feature, index) => (
                      <li key={index} className="flex items-center text-sm text-gray-600">
                        <CheckCircle className="h-3 w-3 text-green-500 mr-2 flex-shrink-0" />
                        {feature}
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Suitable For */}
                <div>
                  <h4 className="font-medium text-gray-900 mb-2">Suitable For:</h4>
                  <div className="flex flex-wrap gap-1">
                    {plan.suitableFor.map((item, index) => (
                      <Badge key={index} variant="outline" className="text-xs">
                        {item}
                      </Badge>
                    ))}
                  </div>
                </div>

                {/* Health Conditions */}
                {plan.diseases.length > 0 && (
                  <div>
                    <h4 className="font-medium text-gray-900 mb-2 flex items-center">
                      <Heart className="h-4 w-4 mr-1 text-red-500" />
                      Addresses:
                    </h4>
                    <div className="flex flex-wrap gap-1">
                      {plan.diseases.map((disease, index) => (
                        <Badge key={index} className="bg-red-100 text-red-800 text-xs">
                          {disease}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}

                {/* Actions */}
                <div className="flex gap-3 pt-4 border-t">
                  <Button 
                    variant="outline" 
                    className="flex-1"
                    onClick={() => handleViewSample(plan.id)}
                  >
                    <Eye className="h-4 w-4 mr-2" />
                    View Sample
                  </Button>
                  <Button 
                    className="flex-1"
                    onClick={() => handleSubscribe(requirement.type)}
                  >
                    <CreditCard className="h-4 w-4 mr-2" />
                    Get This Plan
                  </Button>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Call to Action */}
      <div className="mt-16 text-center">
        <Card className="bg-gradient-to-r from-blue-50 to-purple-50 border-none">
          <CardContent className="py-12">
            <h3 className="text-2xl font-bold text-gray-900 mb-4">
              Ready to Transform Your Health?
            </h3>
            <p className="text-lg text-gray-600 mb-8 max-w-2xl mx-auto">
              Join thousands of satisfied customers who have achieved their health goals 
              with our personalized nutrition plans.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button size="lg" onClick={() => handleSubscribe('professional')}>
                <CreditCard className="h-5 w-5 mr-2" />
                Start Professional Plan
              </Button>
              <Button size="lg" variant="outline" onClick={() => navigate('/nutrition')}>
                <Calculator className="h-5 w-5 mr-2" />
                Try Free Calculator
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default PublicNutritionPlans;
