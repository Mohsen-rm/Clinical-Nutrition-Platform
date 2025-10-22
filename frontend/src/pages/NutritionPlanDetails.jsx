import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { 
  ArrowLeft, 
  User, 
  Calendar, 
  Target, 
  Activity, 
  Heart, 
  Calculator,
  Utensils,
  AlertCircle,
  Pill,
  MessageCircle,
  Download,
  Edit
} from 'lucide-react';
import { nutritionAPI } from '../lib/api';
import useAuthStore from '../store/authStore';
import { useToast } from '../components/ui/use-toast';

const NutritionPlanDetails = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { isDoctor, user } = useAuthStore();
  const { toast } = useToast();

  // Fetch plan details
  const { data: planResponse, isLoading, error } = useQuery({
    queryKey: ['nutrition-plan', id],
    queryFn: () => nutritionAPI.getPlan(id),
    enabled: !!id,
  });

  const plan = planResponse?.data?.nutrition_plan;

  if (isLoading) {
    return (
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="animate-pulse space-y-6">
          <div className="h-8 bg-gray-200 rounded w-1/3"></div>
          <div className="grid md:grid-cols-2 gap-6">
            <div className="h-64 bg-gray-200 rounded"></div>
            <div className="h-64 bg-gray-200 rounded"></div>
          </div>
        </div>
      </div>
    );
  }

  if (error || !plan) {
    return (
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Card>
          <CardContent className="text-center py-12">
            <AlertCircle className="h-12 w-12 mx-auto mb-4 text-red-500" />
            <h3 className="text-lg font-semibold mb-2">Plan Not Found</h3>
            <p className="text-gray-600 mb-4">
              The nutrition plan you're looking for doesn't exist or you don't have permission to view it.
            </p>
            <Button onClick={() => navigate('/nutrition')}>
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Nutrition Plans
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  const getGoalColor = (goal) => {
    switch (goal) {
      case 'lose': return 'bg-red-100 text-red-800';
      case 'gain': return 'bg-green-100 text-green-800';
      case 'maintain': return 'bg-blue-100 text-blue-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getGoalText = (goal) => {
    switch (goal) {
      case 'lose': return 'Lose Weight';
      case 'gain': return 'Gain Weight';
      case 'maintain': return 'Maintain Weight';
      default: return goal;
    }
  };

  const getActivityLevelText = (level) => {
    switch (level) {
      case 'sedentary': return 'Sedentary';
      case 'light': return 'Lightly Active';
      case 'moderate': return 'Moderately Active';
      case 'active': return 'Very Active';
      case 'extra': return 'Extra Active';
      default: return level;
    }
  };

  const handleSendWhatsApp = () => {
    // Navigate to WhatsApp integration or show modal
    toast({
      title: "WhatsApp Integration",
      description: "WhatsApp messaging feature will be available soon!",
    });
  };

  const handleDownloadPlan = () => {
    // Generate PDF or export functionality
    toast({
      title: "Download Plan",
      description: "Plan download feature will be available soon!",
    });
  };

  const handleEditPlan = () => {
    // Navigate to edit page or show modal
    toast({
      title: "Edit Plan",
      description: "Plan editing feature will be available soon!",
    });
  };

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-4 mb-4">
          <Button 
            variant="outline" 
            size="sm"
            onClick={() => navigate('/nutrition')}
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back
          </Button>
          <div className="flex-1">
            <h1 className="text-3xl font-bold text-gray-900">
              {plan.name || `Nutrition Plan #${plan.id}`}
            </h1>
            <p className="text-gray-600 mt-1">
              Created on {new Date(plan.created_at).toLocaleDateString()}
            </p>
          </div>
          <div className="flex gap-2">
            {isDoctor() && (
              <>
                <Button variant="outline" size="sm" onClick={handleEditPlan}>
                  <Edit className="h-4 w-4 mr-2" />
                  Edit
                </Button>
                <Button variant="outline" size="sm" onClick={handleSendWhatsApp}>
                  <MessageCircle className="h-4 w-4 mr-2" />
                  WhatsApp
                </Button>
              </>
            )}
            <Button variant="outline" size="sm" onClick={handleDownloadPlan}>
              <Download className="h-4 w-4 mr-2" />
              Download
            </Button>
          </div>
        </div>
      </div>

      <div className="grid lg:grid-cols-3 gap-8">
        {/* Left Column - Patient Info & Goals */}
        <div className="lg:col-span-1 space-y-6">
          {/* Patient Information */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <User className="h-5 w-5" />
                Patient Information
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium text-gray-500">Age</label>
                  <p className="text-lg font-semibold">{plan.age} years</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-500">Gender</label>
                  <p className="text-lg font-semibold capitalize">{plan.gender}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-500">Weight</label>
                  <p className="text-lg font-semibold">{plan.weight} kg</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-500">Height</label>
                  <p className="text-lg font-semibold">{plan.height} cm</p>
                </div>
              </div>
              
              <div>
                <label className="text-sm font-medium text-gray-500">Activity Level</label>
                <p className="text-lg font-semibold">{getActivityLevelText(plan.activity_level)}</p>
              </div>
              
              <div>
                <label className="text-sm font-medium text-gray-500">Goal</label>
                <Badge className={`${getGoalColor(plan.goal)} mt-1`}>
                  <Target className="h-3 w-3 mr-1" />
                  {getGoalText(plan.goal)}
                </Badge>
              </div>
            </CardContent>
          </Card>

          {/* Health Conditions */}
          {plan.diseases && plan.diseases.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Heart className="h-5 w-5" />
                  Health Conditions
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {plan.diseases.map((disease) => (
                    <div key={disease.id} className="p-3 border rounded-lg">
                      <div className="font-medium text-sm">{disease.name}</div>
                      <div className="text-xs text-gray-600 mt-1">
                        {disease.description}
                      </div>
                      <div className="text-xs text-gray-500 mt-1">
                        Calorie adjustment: {disease.calorie_adjustment > 0 ? '+' : ''}{disease.calorie_adjustment}
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Additional Information */}
          {(plan.allergies || plan.medications) && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <AlertCircle className="h-5 w-5" />
                  Additional Information
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {plan.allergies && (
                  <div>
                    <label className="text-sm font-medium text-gray-500">Allergies</label>
                    <p className="text-sm mt-1">{plan.allergies}</p>
                  </div>
                )}
                {plan.medications && (
                  <div>
                    <label className="text-sm font-medium text-gray-500 flex items-center gap-1">
                      <Pill className="h-3 w-3" />
                      Medications
                    </label>
                    <p className="text-sm mt-1">{plan.medications}</p>
                  </div>
                )}
              </CardContent>
            </Card>
          )}
        </div>

        {/* Right Column - Nutrition Details */}
        <div className="lg:col-span-2 space-y-6">
          {/* Caloric Requirements */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Calculator className="h-5 w-5" />
                Caloric Requirements
              </CardTitle>
              <CardDescription>
                Calculated based on personal data and health conditions
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-3 gap-6">
                <div className="text-center p-4 bg-blue-50 rounded-lg">
                  <div className="text-2xl font-bold text-blue-600">{Math.round(plan.bmr)}</div>
                  <div className="text-sm text-blue-800 font-medium">BMR</div>
                  <div className="text-xs text-blue-600">Basal Metabolic Rate</div>
                </div>
                <div className="text-center p-4 bg-green-50 rounded-lg">
                  <div className="text-2xl font-bold text-green-600">{Math.round(plan.tdee)}</div>
                  <div className="text-sm text-green-800 font-medium">TDEE</div>
                  <div className="text-xs text-green-600">Total Daily Energy</div>
                </div>
                <div className="text-center p-4 bg-purple-50 rounded-lg">
                  <div className="text-2xl font-bold text-purple-600">{Math.round(plan.target_calories)}</div>
                  <div className="text-sm text-purple-800 font-medium">Target</div>
                  <div className="text-xs text-purple-600">Daily Calories</div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Macronutrient Breakdown */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Utensils className="h-5 w-5" />
                Macronutrient Breakdown
              </CardTitle>
              <CardDescription>
                Daily macronutrient targets based on your caloric needs
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-3 gap-6">
                <div className="text-center p-4 border rounded-lg">
                  <div className="text-2xl font-bold text-red-600">{Math.round(plan.protein_grams)}g</div>
                  <div className="text-sm font-medium text-red-800">Protein</div>
                  <div className="text-xs text-gray-600">
                    {Math.round((plan.protein_grams * 4 / plan.target_calories) * 100)}% of calories
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                    <div 
                      className="bg-red-500 h-2 rounded-full" 
                      style={{ width: `${(plan.protein_grams * 4 / plan.target_calories) * 100}%` }}
                    ></div>
                  </div>
                </div>
                <div className="text-center p-4 border rounded-lg">
                  <div className="text-2xl font-bold text-yellow-600">{Math.round(plan.carbs_grams)}g</div>
                  <div className="text-sm font-medium text-yellow-800">Carbohydrates</div>
                  <div className="text-xs text-gray-600">
                    {Math.round((plan.carbs_grams * 4 / plan.target_calories) * 100)}% of calories
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                    <div 
                      className="bg-yellow-500 h-2 rounded-full" 
                      style={{ width: `${(plan.carbs_grams * 4 / plan.target_calories) * 100}%` }}
                    ></div>
                  </div>
                </div>
                <div className="text-center p-4 border rounded-lg">
                  <div className="text-2xl font-bold text-green-600">{Math.round(plan.fat_grams)}g</div>
                  <div className="text-sm font-medium text-green-800">Fats</div>
                  <div className="text-xs text-gray-600">
                    {Math.round((plan.fat_grams * 9 / plan.target_calories) * 100)}% of calories
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                    <div 
                      className="bg-green-500 h-2 rounded-full" 
                      style={{ width: `${(plan.fat_grams * 9 / plan.target_calories) * 100}%` }}
                    ></div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Meal Plan */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Utensils className="h-5 w-5" />
                Meal Plan
              </CardTitle>
              <CardDescription>
                Suggested meal structure and timing
              </CardDescription>
            </CardHeader>
            <CardContent>
              {plan.meal_plan && Object.keys(plan.meal_plan).length > 0 ? (
                <div className="space-y-4">
                  {Object.entries(plan.meal_plan).map(([meal, details]) => (
                    <div key={meal} className="p-4 border rounded-lg">
                      <h4 className="font-medium capitalize mb-2">{meal}</h4>
                      <p className="text-sm text-gray-600">{details}</p>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <Utensils className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p className="mb-2">No specific meal plan created yet</p>
                  <p className="text-sm">
                    Focus on meeting your daily caloric and macronutrient targets
                  </p>
                  {isDoctor() && (
                    <Button variant="outline" size="sm" className="mt-4" onClick={handleEditPlan}>
                      Add Meal Plan
                    </Button>
                  )}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Notes */}
          {plan.notes && (
            <Card>
              <CardHeader>
                <CardTitle>Notes</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-gray-700 whitespace-pre-wrap">{plan.notes}</p>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
};

export default NutritionPlanDetails;
