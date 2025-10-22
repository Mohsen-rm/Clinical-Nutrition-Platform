import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { 
  Calculator, 
  Heart, 
  Activity, 
  Eye, 
  CreditCard,
  BookOpen,
  Target,
  TrendingUp,
  Info,
  Lock,
  Star
} from 'lucide-react';
import { nutritionAPI, subscriptionAPI } from '../../lib/api';
import { useToast } from '../ui/use-toast';
import { useNavigate } from 'react-router-dom';
import useAuthStore from '../../store/authStore';

const PatientNutritionView = () => {
  const { toast } = useToast();
  const navigate = useNavigate();
  const { user } = useAuthStore();
  const [calculatorData, setCalculatorData] = useState({
    age: '',
    weight: '',
    height: '',
    gender: 'male',
    activity_level: 'moderate',
    goal: 'maintain'
  });

  // Fetch patient's nutrition plans only
  const { data: nutritionPlansResponse } = useQuery({
    queryKey: ['nutrition-plans'],
    queryFn: nutritionAPI.getPlans,
  });

  // Fetch subscription status
  const { data: subscriptionResponse } = useQuery({
    queryKey: ['subscription-status'],
    queryFn: subscriptionAPI.getStatus,
  });

  const nutritionPlans = nutritionPlansResponse?.data?.nutrition_plans || [];
  const subscription = subscriptionResponse?.data?.subscription;

  const handleInputChange = (field, value) => {
    setCalculatorData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleCalculateBasic = () => {
    // Basic BMR calculation for patients
    const { age, weight, height, gender } = calculatorData;
    
    if (!age || !weight || !height) {
      toast({
        title: "Missing Information",
        description: "Please fill in all fields to calculate your needs",
        variant: "destructive",
      });
      return;
    }

    // Mifflin-St Jeor Equation
    let bmr;
    if (gender === 'male') {
      bmr = 10 * weight + 6.25 * height - 5 * age + 5;
    } else {
      bmr = 10 * weight + 6.25 * height - 5 * age - 161;
    }

    // Activity multiplier
    const activityMultipliers = {
      sedentary: 1.2,
      light: 1.375,
      moderate: 1.55,
      active: 1.725,
      extra: 1.9
    };

    const tdee = Math.round(bmr * activityMultipliers[calculatorData.activity_level]);

    toast({
      title: "Your Daily Calorie Needs",
      description: `Approximately ${tdee} calories per day`,
    });
  };

  const handleSubscribe = () => {
    navigate('/subscription');
  };

  const handleViewDetails = (planId) => {
    navigate(`/nutrition/plan/${planId}`);
  };

  const handleViewPlans = () => {
    navigate('/plans');
  };

  // Educational content for patients
  const educationalTips = [
    {
      title: "Balanced Nutrition",
      description: "Include proteins, carbohydrates, and healthy fats in every meal",
      icon: <Target className="h-5 w-5 text-green-600" />
    },
    {
      title: "Stay Hydrated",
      description: "Drink at least 8 glasses of water daily for optimal health",
      icon: <Heart className="h-5 w-5 text-blue-600" />
    },
    {
      title: "Regular Exercise",
      description: "Combine good nutrition with regular physical activity",
      icon: <Activity className="h-5 w-5 text-orange-600" />
    },
    {
      title: "Portion Control",
      description: "Use smaller plates and listen to your body's hunger cues",
      icon: <TrendingUp className="h-5 w-5 text-purple-600" />
    }
  ];

  return (
    <div className="space-y-8">
      {/* Patient Header */}
      <div className="bg-gradient-to-r from-green-500 to-blue-500 text-white p-6 rounded-lg">
        <div className="flex items-center gap-3 mb-4">
          <Heart className="h-8 w-8" />
          <div>
            <h1 className="text-2xl font-bold">Your Nutrition Journey</h1>
            <p className="text-green-100">Track your health and achieve your nutrition goals</p>
          </div>
        </div>
        
        {/* Patient Stats */}
        <div className="grid md:grid-cols-3 gap-4 mt-6">
          <div className="bg-white/10 backdrop-blur-sm rounded-lg p-4">
            <div className="flex items-center gap-2">
              <Activity className="h-5 w-5" />
              <span className="text-sm font-medium">My Plans</span>
            </div>
            <div className="text-2xl font-bold mt-1">{nutritionPlans.length}</div>
          </div>
          <div className="bg-white/10 backdrop-blur-sm rounded-lg p-4">
            <div className="flex items-center gap-2">
              <Star className="h-5 w-5" />
              <span className="text-sm font-medium">Subscription</span>
            </div>
            <div className="text-sm font-bold mt-1">
              {subscription?.is_active ? subscription.plan_name : 'Free Plan'}
            </div>
          </div>
          <div className="bg-white/10 backdrop-blur-sm rounded-lg p-4">
            <div className="flex items-center gap-2">
              <Target className="h-5 w-5" />
              <span className="text-sm font-medium">Goal</span>
            </div>
            <div className="text-sm font-bold mt-1">Healthy Living</div>
          </div>
        </div>
      </div>

      {/* Subscription Notice */}
      {!subscription?.is_active && (
        <Card className="border-blue-200 bg-blue-50">
          <CardContent className="p-6">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-blue-100 rounded-full">
                <CreditCard className="h-6 w-6 text-blue-600" />
              </div>
              <div className="flex-1">
                <h3 className="font-semibold text-blue-900 mb-1">Unlock Professional Nutrition Plans</h3>
                <p className="text-blue-700 text-sm mb-3">
                  Get personalized nutrition plans created by certified nutritionists, 
                  detailed meal recommendations, and ongoing support.
                </p>
                <div className="flex gap-2">
                  <Button onClick={handleSubscribe} size="sm">
                    <CreditCard className="h-4 w-4 mr-2" />
                    Subscribe Now
                  </Button>
                  <Button onClick={handleViewPlans} variant="outline" size="sm">
                    <BookOpen className="h-4 w-4 mr-2" />
                    View Plans
                  </Button>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      <div className="grid lg:grid-cols-3 gap-8">
        {/* Basic Calorie Calculator */}
        <div className="lg:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Calculator className="h-5 w-5" />
                Basic Calorie Calculator
              </CardTitle>
              <CardDescription>
                Get an estimate of your daily calorie needs
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium">Age</label>
                  <Input
                    type="number"
                    placeholder="25"
                    value={calculatorData.age}
                    onChange={(e) => handleInputChange('age', e.target.value)}
                  />
                </div>
                <div>
                  <label className="text-sm font-medium">Gender</label>
                  <select
                    className="w-full p-2 border rounded-md"
                    value={calculatorData.gender}
                    onChange={(e) => handleInputChange('gender', e.target.value)}
                  >
                    <option value="male">Male</option>
                    <option value="female">Female</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium">Weight (kg)</label>
                  <Input
                    type="number"
                    placeholder="70"
                    value={calculatorData.weight}
                    onChange={(e) => handleInputChange('weight', e.target.value)}
                  />
                </div>
                <div>
                  <label className="text-sm font-medium">Height (cm)</label>
                  <Input
                    type="number"
                    placeholder="175"
                    value={calculatorData.height}
                    onChange={(e) => handleInputChange('height', e.target.value)}
                  />
                </div>
              </div>

              <div>
                <label className="text-sm font-medium">Activity Level</label>
                <select
                  className="w-full p-2 border rounded-md"
                  value={calculatorData.activity_level}
                  onChange={(e) => handleInputChange('activity_level', e.target.value)}
                >
                  <option value="sedentary">Sedentary (little/no exercise)</option>
                  <option value="light">Light (light exercise 1-3 days/week)</option>
                  <option value="moderate">Moderate (moderate exercise 3-5 days/week)</option>
                  <option value="active">Active (hard exercise 6-7 days/week)</option>
                  <option value="extra">Extra Active (very hard exercise, physical job)</option>
                </select>
              </div>

              <div>
                <label className="text-sm font-medium">Goal</label>
                <select
                  className="w-full p-2 border rounded-md"
                  value={calculatorData.goal}
                  onChange={(e) => handleInputChange('goal', e.target.value)}
                >
                  <option value="lose">Lose Weight</option>
                  <option value="maintain">Maintain Weight</option>
                  <option value="gain">Gain Weight</option>
                </select>
              </div>

              <Button 
                onClick={handleCalculateBasic}
                className="w-full"
              >
                <Calculator className="h-4 w-4 mr-2" />
                Calculate My Needs
              </Button>

              {/* Professional Features Locked */}
              {!subscription?.is_active && (
                <div className="mt-6 p-4 border-2 border-dashed border-gray-300 rounded-lg bg-gray-50">
                  <div className="text-center">
                    <Lock className="h-8 w-8 mx-auto mb-2 text-gray-400" />
                    <h4 className="font-medium text-gray-700 mb-1">Professional Features</h4>
                    <p className="text-sm text-gray-600 mb-3">
                      Health conditions, detailed analysis, and personalized meal plans
                    </p>
                    <Button onClick={handleSubscribe} size="sm">
                      Unlock Professional Features
                    </Button>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Educational Content */}
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BookOpen className="h-5 w-5" />
                Nutrition Tips
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {educationalTips.map((tip, index) => (
                <div key={index} className="flex items-start gap-3">
                  <div className="mt-1">{tip.icon}</div>
                  <div>
                    <h4 className="font-medium text-sm">{tip.title}</h4>
                    <p className="text-xs text-gray-600 mt-1">{tip.description}</p>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>

          {/* Quick Actions */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Target className="h-5 w-5" />
                Quick Actions
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <Button variant="outline" className="w-full justify-start" onClick={handleViewPlans}>
                <BookOpen className="h-4 w-4 mr-2" />
                Browse Nutrition Plans
              </Button>
              {!subscription?.is_active && (
                <Button variant="outline" className="w-full justify-start" onClick={handleSubscribe}>
                  <CreditCard className="h-4 w-4 mr-2" />
                  Upgrade Subscription
                </Button>
              )}
              <Button variant="outline" className="w-full justify-start">
                <Info className="h-4 w-4 mr-2" />
                Learn About Nutrition
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* My Nutrition Plans */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="h-5 w-5" />
            My Nutrition Plans
          </CardTitle>
          <CardDescription>
            Personalized nutrition plans created for you
          </CardDescription>
        </CardHeader>
        <CardContent>
          {nutritionPlans?.length > 0 ? (
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
              {nutritionPlans.map((plan) => (
                <div key={plan.id} className="p-4 border rounded-lg hover:shadow-md transition-shadow">
                  <h4 className="font-medium mb-2">
                    {plan.name || `My Plan #${plan.id}`}
                  </h4>
                  <div className="text-sm text-gray-600 space-y-1">
                    <div>Target: {plan.goal}</div>
                    <div>Calories: {Math.round(plan.target_calories)}/day</div>
                    <div>Created: {new Date(plan.created_at).toLocaleDateString()}</div>
                    {plan.diseases && plan.diseases.length > 0 && (
                      <div className="text-xs text-blue-600">
                        Addresses {plan.diseases.length} health condition{plan.diseases.length > 1 ? 's' : ''}
                      </div>
                    )}
                  </div>
                  <Button 
                    size="sm" 
                    variant="outline" 
                    className="w-full mt-3"
                    onClick={() => handleViewDetails(plan.id)}
                  >
                    <Eye className="h-3 w-3 mr-1" />
                    View My Plan
                  </Button>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              <Activity className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p className="mb-2">No nutrition plans yet</p>
              <p className="text-sm mb-4">
                Subscribe to get personalized nutrition plans created by professional nutritionists
              </p>
              <div className="flex gap-2 justify-center">
                <Button onClick={handleSubscribe}>
                  <CreditCard className="h-4 w-4 mr-2" />
                  Get Started
                </Button>
                <Button onClick={handleViewPlans} variant="outline">
                  <BookOpen className="h-4 w-4 mr-2" />
                  Browse Plans
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default PatientNutritionView;
