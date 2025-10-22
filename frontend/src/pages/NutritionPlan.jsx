import React from 'react';
import useAuthStore from '../store/authStore';
import AdminNutritionView from '../components/nutrition/AdminNutritionView';
import DoctorNutritionView from '../components/nutrition/DoctorNutritionView';
import PatientNutritionView from '../components/nutrition/PatientNutritionView';

const NutritionPlan = () => {
  const { isDoctor, isAdmin, user, isAuthenticated } = useAuthStore();

  // Return appropriate view based on user role
  if (!isAuthenticated) {
    return (
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">
            Please log in to access nutrition planning
          </h1>
          <p className="text-gray-600">
            You need to be logged in to view your nutrition plans and use our tools.
          </p>
        </div>
      </div>
    );
  }

  // Admin gets full system access
  if (isAdmin()) {
    return <AdminNutritionView />;
  }

  // Doctor gets professional tools
  if (isDoctor()) {
    return <DoctorNutritionView />;
  }

  // Patient gets simplified view
  return <PatientNutritionView />;
};

export default NutritionPlan;
