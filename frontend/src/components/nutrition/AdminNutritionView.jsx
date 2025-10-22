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
  BarChart3,
  Settings,
  Database,
  Shield
} from 'lucide-react';
import { nutritionAPI } from '../../lib/api';
import { useToast } from '../ui/use-toast';
import { useNavigate } from 'react-router-dom';

const AdminNutritionView = () => {
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

  // Fetch all nutrition plans (admin can see all)
  const { data: nutritionPlansResponse } = useQuery({
    queryKey: ['nutrition-plans'],
    queryFn: nutritionAPI.getPlans,
  });

  // Fetch demo data
  const { data: demoResponse } = useQuery({
    queryKey: ['nutrition-demo'],
    queryFn: nutritionAPI.getDemo,
  });

  const diseases = diseasesResponse?.data?.diseases || [];
  const nutritionPlans = nutritionPlansResponse?.data?.nutrition_plans || [];
  const demoData = demoResponse?.data;

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
      name: `Admin Plan - ${new Date().toLocaleDateString()}`,
      diseases: calculatorData.diseases
    };
    createPlanMutation.mutate(planData);
  };

  const handleViewDetails = (planId) => {
    navigate(`/nutrition/plan/${planId}`);
  };

  // Admin-specific statistics
  const totalPlans = nutritionPlans.length;
  const uniquePatients = new Set(nutritionPlans.map(plan => plan.patient_id)).size;
  const plansThisMonth = nutritionPlans.filter(plan => {
    const planDate = new Date(plan.created_at);
    const now = new Date();
    return planDate.getMonth() === now.getMonth() && planDate.getFullYear() === now.getFullYear();
  }).length;

  return (
    <div className="space-y-8">
      {/* Admin Header */}
      <div className="bg-gradient-to-r from-purple-600 to-blue-600 text-white p-6 rounded-lg">
        <div className="flex items-center gap-3 mb-4">
          <Shield className="h-8 w-8" />
          <div>
            <h1 className="text-2xl font-bold">Admin Nutrition Management</h1>
            <p className="text-purple-100">Complete system oversight and management</p>
          </div>
        </div>
        
        {/* Admin Stats */}
        <div className="grid md:grid-cols-4 gap-4 mt-6">
          <div className="bg-white/10 backdrop-blur-sm rounded-lg p-4">
            <div className="flex items-center gap-2">
              <Activity className="h-5 w-5" />
              <span className="text-sm font-medium">Total Plans</span>
            </div>
            <div className="text-2xl font-bold mt-1">{totalPlans}</div>
          </div>
          <div className="bg-white/10 backdrop-blur-sm rounded-lg p-4">
            <div className="flex items-center gap-2">
              <Users className="h-5 w-5" />
              <span className="text-sm font-medium">Unique Patients</span>
            </div>
            <div className="text-2xl font-bold mt-1">{uniquePatients}</div>
          </div>
          <div className="bg-white/10 backdrop-blur-sm rounded-lg p-4">
            <div className="flex items-center gap-2">
              <BarChart3 className="h-5 w-5" />
              <span className="text-sm font-medium">This Month</span>
            </div>
            <div className="text-2xl font-bold mt-1">{plansThisMonth}</div>
          </div>
          <div className="bg-white/10 backdrop-blur-sm rounded-lg p-4">
            <div className="flex items-center gap-2">
              <Database className="h-5 w-5" />
              <span className="text-sm font-medium">Diseases</span>
            </div>
            <div className="text-2xl font-bold mt-1">{diseases.length}</div>
          </div>
        </div>
      </div>

      <div className="grid lg:grid-cols-2 gap-8">
        {/* Advanced Calorie Calculator */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Calculator className="h-5 w-5" />
              Advanced Nutrition Calculator
            </CardTitle>
            <CardDescription>
              Create comprehensive nutrition plans with full administrative controls
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
              <div className="grid grid-cols-2 gap-2 max-h-32 overflow-y-auto">
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

            {/* Additional Fields */}
            <div>
              <label className="text-sm font-medium">Allergies</label>
              <Input
                placeholder="Food allergies or intolerances"
                value={calculatorData.allergies}
                onChange={(e) => handleInputChange('allergies', e.target.value)}
              />
            </div>

            <div>
              <label className="text-sm font-medium">Medications</label>
              <Input
                placeholder="Current medications"
                value={calculatorData.medications}
                onChange={(e) => handleInputChange('medications', e.target.value)}
              />
            </div>

            <div>
              <label className="text-sm font-medium">Notes</label>
              <textarea
                className="w-full p-2 border rounded-md"
                rows="3"
                placeholder="Additional notes or special considerations"
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
                Calculate Only
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

        {/* System Management */}
        <div className="space-y-6">
          {/* Quick Actions */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Settings className="h-5 w-5" />
                System Management
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <Button variant="outline" className="w-full justify-start">
                <Database className="h-4 w-4 mr-2" />
                Manage Diseases & Conditions
              </Button>
              <Button variant="outline" className="w-full justify-start">
                <Users className="h-4 w-4 mr-2" />
                User Management
              </Button>
              <Button variant="outline" className="w-full justify-start">
                <BarChart3 className="h-4 w-4 mr-2" />
                System Analytics
              </Button>
              <Button variant="outline" className="w-full justify-start">
                <MessageCircle className="h-4 w-4 mr-2" />
                WhatsApp Configuration
              </Button>
            </CardContent>
          </Card>

          {/* Demo Data */}
          {demoData && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Heart className="h-5 w-5" />
                  Disease Impact Demo
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3 text-sm">
                  <div className="flex justify-between">
                    <span>Base TDEE:</span>
                    <span className="font-medium">{demoData.base_tdee} calories</span>
                  </div>
                  <div className="flex justify-between">
                    <span>With Diseases:</span>
                    <span className="font-medium">{demoData.adjusted_calories} calories</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Adjustment:</span>
                    <span className="font-medium text-red-600">{demoData.total_adjustment} calories</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>

      {/* All Nutrition Plans */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="h-5 w-5" />
            All Nutrition Plans
          </CardTitle>
          <CardDescription>
            Complete overview of all nutrition plans in the system
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
                    <div>Patient ID: {plan.patient_id}</div>
                    <div>Doctor ID: {plan.doctor_id}</div>
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
                  <Button 
                    size="sm" 
                    variant="outline" 
                    className="w-full mt-3"
                    onClick={() => handleViewDetails(plan.id)}
                  >
                    <Eye className="h-3 w-3 mr-1" />
                    View Details
                  </Button>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              <Activity className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p className="mb-2">No nutrition plans yet</p>
              <p className="text-sm">Plans created by doctors will appear here</p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default AdminNutritionView;
