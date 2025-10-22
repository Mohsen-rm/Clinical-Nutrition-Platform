#!/usr/bin/env python
import os
import sys
import django

# Add the backend directory to Python path
sys.path.append('/Users/mohsen/Desktop/Clinical_Nutrition_Platform/backend')

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clinical_platform.settings')
django.setup()

from apps.nutrition.models import NutritionPlan, Disease
from apps.accounts.models import User

def test_disease_adjustments():
    """Test that disease adjustments are properly applied"""
    
    # Get a user
    user = User.objects.filter(user_type='doctor').first()
    if not user:
        print("❌ No doctor user found")
        return
    
    # Create a nutrition plan without diseases first
    plan_data = {
        'patient': user,
        'doctor': user,
        'age': 25,
        'gender': 'male',
        'height': 175.0,
        'weight': 70.0,
        'activity_level': 'moderate',
        'goal': 'maintain',
        'name': 'Test Plan'
    }
    
    plan = NutritionPlan.objects.create(**plan_data)
    
    print(f"📊 Plan created with ID: {plan.id}")
    print(f"Base TDEE: {plan.tdee}")
    print(f"Base Target Calories: {plan.target_calories}")
    
    # Add diseases
    diseases = Disease.objects.filter(id__in=[5, 6])  # Cardiovascular (-100) + Kidney (-50)
    plan.diseases.set(diseases)
    
    print(f"\n🏥 Added diseases:")
    for disease in diseases:
        print(f"  - {disease.name}: {disease.calorie_adjustment} calories")
    
    # Apply adjustments
    plan.apply_disease_adjustments()
    
    # Refresh from database
    plan.refresh_from_db()
    
    print(f"\n📈 After disease adjustments:")
    print(f"Adjusted Target Calories: {plan.target_calories}")
    print(f"Expected: {plan.tdee - 150} (TDEE - 150)")
    print(f"Protein: {plan.protein_grams}g")
    print(f"Carbs: {plan.carbs_grams}g")
    print(f"Fat: {plan.fat_grams}g")
    
    # Verify the adjustment
    expected_calories = plan.tdee - 150  # -100 (cardiovascular) + -50 (kidney)
    if abs(plan.target_calories - expected_calories) < 0.01:
        print("✅ Disease adjustments applied correctly!")
    else:
        print(f"❌ Disease adjustments not applied correctly. Expected: {expected_calories}, Got: {plan.target_calories}")

if __name__ == '__main__':
    test_disease_adjustments()
