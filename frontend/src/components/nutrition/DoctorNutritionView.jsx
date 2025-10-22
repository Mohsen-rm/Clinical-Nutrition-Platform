import React, { useState } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { 
  Calculator, 
  Heart, 
  Activity, 
  Plus, 
  Eye, 
  MessageCircle, 
  Users,
  Stethoscope,
  ClipboardList,
  TrendingUp
} from 'lucide-react';
import { nutritionAPI } from '../../lib/api';
import { useToast } from '../ui/use-toast';
import { useNavigate } from 'react-router-dom';

const DoctorNutritionView = () => {
  const { toast } = useToast();
  const navigate = useNavigate();
  const [calculatorData, setCalculatorData] = useState({
    age: '',
    weight: '',
    height: '',
    gender: 'male',
    activity_level: 'moderate',
    goal: 'maintain',
    diseases: [],
    allergies: '',
    medications: '',
    notes: ''
  });

  // Fetch diseases
  const { data: diseasesResponse } = useQuery({
    queryKey: ['diseases'],
    queryFn: nutritionAPI.getDiseases,
  });

  // Fetch doctor's nutrition plans only
  const { data: nutritionPlansResponse } = useQuery({
    queryKey: ['nutrition-plans'],
    queryFn: nutritionAPI.getPlans,
  });

  // Fetch demo data
  const { data: demoResponse } = useQuery({
    queryKey: ['nutrition-demo'],
    queryFn: nutritionAPI.getDemo,
  });

  // Fetch WhatsApp messages
  const { data: whatsappResponse } = useQuery({
    queryKey: ['whatsapp-messages'],
    queryFn: nutritionAPI.getWhatsAppMessages,
  });

  const diseases = diseasesResponse?.data?.diseases || [];
  const nutritionPlans = nutritionPlansResponse?.data?.nutrition_plans || [];
  const demoData = demoResponse?.data;
  const whatsappMessages = whatsappResponse?.data?.messages || [];

  // Calculate calories mutation
  const calculateMutation = useMutation({
    mutationFn: nutritionAPI.calculateCalories,
    onSuccess: (response) => {
      toast({
        title: "Calculation complete",
        description: `Recommended daily calories: ${response.data.recommended_calories}`,
      });
    },
    onError: (error) => {
      toast({
        title: "Calculation failed",
        description: error.response?.data?.error || "Please try again",
        variant: "destructive",
      });
    },
  });

  // Create plan mutation
  const createPlanMutation = useMutation({
    mutationFn: nutritionAPI.createPlan,
    onSuccess: (response) => {
      toast({
        title: "Plan created successfully",
        description: "Nutrition plan has been created for the patient",
      });
      // Reset form
      setCalculatorData({
        age: '',
        weight: '',
        height: '',
        gender: 'male',
        activity_level: 'moderate',
        goal: 'maintain',
        diseases: [],
        allergies: '',
        medications: '',
        notes: ''
      });
    },
    onError: (error) => {
      toast({
        title: "Failed to create plan",
        description: error.response?.data?.error || "Please try again",
        variant: "destructive",
      });
    },
  });

  const handleInputChange = (field, value) => {
    setCalculatorData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleDiseaseChange = (diseaseId, checked) => {
    setCalculatorData(prev => ({
      ...prev,
      diseases: checked 
        ? [...prev.diseases, diseaseId]
        : prev.diseases.filter(id => id !== diseaseId)
    }));
  };

  const handleCalculate = () => {
    calculateMutation.mutate(calculatorData);
  };

  const handleCreatePlan = () => {
    const planData = {
      ...calculatorData,
      name: `Plan - ${new Date().toLocaleDateString()}`,
      diseases: calculatorData.diseases
    };
    createPlanMutation.mutate(planData);
  };

  const handleViewDetails = (planId) => {
    navigate(`/nutrition/plan/${planId}`);
  };

  // Doctor-specific statistics
  const totalPatients = new Set(nutritionPlans.map(plan => plan.patient_id)).size;
  const plansThisWeek = nutritionPlans.filter(plan => {
    const planDate = new Date(plan.created_at);
    const weekAgo = new Date();
    weekAgo.setDate(weekAgo.getDate() - 7);
    return planDate >= weekAgo;
  }).length;

  return (
    <div className="space-y-8">
      {/* Doctor Header */}
      <div className="bg-gradient-to-r from-blue-600 to-green-600 text-white p-6 rounded-lg">
        <div className="flex items-center gap-3 mb-4">
          <Stethoscope className="h-8 w-8" />
          <div>
            <h1 className="text-2xl font-bold">Doctor's Nutrition Practice</h1>
            <p className="text-blue-100">Create and manage personalized nutrition plans for your patients</p>
          </div>
        </div>
        
        {/* Doctor Stats */}
        <div className="grid md:grid-cols-3 gap-4 mt-6">
          <div className="bg-white/10 backdrop-blur-sm rounded-lg p-4">
            <div className="flex items-center gap-2">
              <Users className="h-5 w-5" />
              <span className="text-sm font-medium">My Patients</span>
            </div>
            <div className="text-2xl font-bold mt-1">{totalPatients}</div>
          </div>
          <div className="bg-white/10 backdrop-blur-sm rounded-lg p-4">
            <div className="flex items-center gap-2">
              <ClipboardList className="h-5 w-5" />
              <span className="text-sm font-medium">Total Plans</span>
            </div>
            <div className="text-2xl font-bold mt-1">{nutritionPlans.length}</div>
          </div>
          <div className="bg-white/10 backdrop-blur-sm rounded-lg p-4">
            <div className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5" />
              <span className="text-sm font-medium">This Week</span>
            </div>
            <div className="text-2xl font-bold mt-1">{plansThisWeek}</div>
          </div>
        </div>
      </div>

      <div className="grid lg:grid-cols-3 gap-8">
        {/* Patient Nutrition Calculator */}
        <div className="lg:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Calculator className="h-5 w-5" />
                Patient Nutrition Calculator
              </CardTitle>
              <CardDescription>
                Create personalized nutrition plans for your patients
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

              {/* Health Conditions */}
              <div>
                <label className="text-sm font-medium mb-2 block">Health Conditions</label>
                <div className="grid grid-cols-2 gap-2 max-h-32 overflow-y-auto border rounded-md p-3">
                  {diseases.map((disease) => (
                    <label key={disease.id} className="flex items-center space-x-2 text-sm">
                      <input
                        type="checkbox"
                        checked={calculatorData.diseases.includes(disease.id)}
                        onChange={(e) => handleDiseaseChange(disease.id, e.target.checked)}
                        className="rounded"
                      />
                      <span>{disease.name}</span>
                    </label>
                  ))}
                </div>
              </div>

              {/* Clinical Information */}
              <div>
                <label className="text-sm font-medium">Allergies & Intolerances</label>
                <Input
                  placeholder="Food allergies or intolerances"
                  value={calculatorData.allergies}
                  onChange={(e) => handleInputChange('allergies', e.target.value)}
                />
              </div>

              <div>
                <label className="text-sm font-medium">Current Medications</label>
                <Input
                  placeholder="Medications that may affect nutrition"
                  value={calculatorData.medications}
                  onChange={(e) => handleInputChange('medications', e.target.value)}
                />
              </div>

              <div>
                <label className="text-sm font-medium">Clinical Notes</label>
                <textarea
                  className="w-full p-2 border rounded-md"
                  rows="3"
                  placeholder="Additional clinical notes or special considerations"
                  value={calculatorData.notes}
                  onChange={(e) => handleInputChange('notes', e.target.value)}
                />
              </div>

              <div className="flex gap-2">
                <Button 
                  onClick={handleCalculate}
                  disabled={calculateMutation.isPending}
                  variant="outline"
                  className="flex-1"
                >
                  <Calculator className="h-4 w-4 mr-2" />
                  Calculate
                </Button>
                <Button 
                  onClick={handleCreatePlan}
                  disabled={createPlanMutation.isPending}
                  className="flex-1"
                >
                  <Plus className="h-4 w-4 mr-2" />
                  Create Plan
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Doctor Tools */}
        <div className="space-y-6">
          {/* Disease Impact Demo */}
          {demoData && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Heart className="h-5 w-5" />
                  Disease Impact Calculator
                </CardTitle>
                <CardDescription>
                  See how medical conditions affect caloric requirements
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3 text-sm">
                  <div className="flex justify-between">
                    <span>Base TDEE:</span>
                    <span className="font-medium">{demoData.base_tdee} cal</span>
                  </div>
                  <div className="flex justify-between">
                    <span>With Conditions:</span>
                    <span className="font-medium">{demoData.adjusted_calories} cal</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Net Adjustment:</span>
                    <span className={`font-medium ${demoData.total_adjustment < 0 ? 'text-red-600' : 'text-green-600'}`}>
                      {demoData.total_adjustment > 0 ? '+' : ''}{demoData.total_adjustment} cal
                    </span>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* WhatsApp Integration */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <MessageCircle className="h-5 w-5" />
                WhatsApp Integration
              </CardTitle>
              <CardDescription>
                Send nutrition plans directly to patients
              </CardDescription>
            </CardHeader>
            <CardContent>
              {whatsappMessages?.length > 0 ? (
                <div className="space-y-2">
                  <p className="text-sm text-gray-600 mb-3">Recent messages:</p>
                  {whatsappMessages.slice(0, 3).map((message, index) => (
                    <div key={index} className="text-xs p-2 bg-gray-50 rounded">
                      {message.content?.substring(0, 50)}...
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-4">
                  <MessageCircle className="h-8 w-8 mx-auto mb-2 text-gray-400" />
                  <p className="text-sm text-gray-600 mb-3">No WhatsApp messages yet</p>
                  <p className="text-xs text-gray-500">
                    Messages will appear here when sent
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Patient Plans */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <ClipboardList className="h-5 w-5" />
            My Patient Plans
          </CardTitle>
          <CardDescription>
            Nutrition plans you've created for your patients
          </CardDescription>
        </CardHeader>
        <CardContent>
          {nutritionPlans?.length > 0 ? (
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
              {nutritionPlans.map((plan) => (
                <div key={plan.id} className="p-4 border rounded-lg hover:shadow-md transition-shadow">
                  <h4 className="font-medium mb-2">
                    {plan.name || `Plan #${plan.id}`}
                  </h4>
                  <div className="text-sm text-gray-600 space-y-1">
                    <div>Age: {plan.age} years</div>
                    <div>Weight: {plan.weight} kg</div>
                    <div>Goal: {plan.goal}</div>
                    <div>Created: {new Date(plan.created_at).toLocaleDateString()}</div>
                    {plan.diseases && plan.diseases.length > 0 && (
                      <div className="text-xs text-blue-600">
                        {plan.diseases.length} health condition{plan.diseases.length > 1 ? 's' : ''}
                      </div>
                    )}
                  </div>
                  <div className="flex gap-2 mt-3">
                    <Button 
                      size="sm" 
                      variant="outline" 
                      className="flex-1"
                      onClick={() => handleViewDetails(plan.id)}
                    >
                      <Eye className="h-3 w-3 mr-1" />
                      View Details
                    </Button>
                    <Button 
                      size="sm" 
                      variant="outline"
                      className="px-3"
                    >
                      <MessageCircle className="h-3 w-3" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              <ClipboardList className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p className="mb-2">No patient plans yet</p>
              <p className="text-sm">Create your first nutrition plan using the calculator above</p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default DoctorNutritionView;
