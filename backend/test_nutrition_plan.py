#!/usr/bin/env python
import os
import sys
import django
import json
import requests

# Add the backend directory to Python path
sys.path.append('/Users/mohsen/Desktop/Clinical_Nutrition_Platform/backend')

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clinical_platform.settings')
django.setup()

def test_nutrition_plan_creation():
    """Test nutrition plan creation with the same data from the error"""
    
    # Login first to get token
    login_url = 'http://localhost:8000/api/auth/login/'
    login_data = {
        'email': 'doctor@example.com',
        'password': 'doctor123'
    }
    
    print("🔐 Logging in...")
    login_response = requests.post(login_url, json=login_data)
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        print(login_response.text)
        return
    
    login_data = login_response.json()
    print(f"Login response: {login_data}")
    
    if 'tokens' in login_data and 'access' in login_data['tokens']:
        token = login_data['tokens']['access']
    elif 'access' in login_data:
        token = login_data['access']
    elif 'access_token' in login_data:
        token = login_data['access_token']
    else:
        print(f"❌ No access token found in response: {login_data}")
        return
        
    print(f"✅ Login successful, token: {token[:20]}...")
    
    # Test nutrition plan creation
    url = 'http://localhost:8000/api/nutrition/plans/'
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # Same data from the error (using diseases as frontend sends)
    data = {
        "age": 25,
        "weight": 70.0,
        "height": 175.0,
        "gender": "male",
        "activity_level": "moderate",
        "goal": "maintain",
        "diseases": [5, 6],  # Frontend sends this
        "name": "Nutrition Plan - 10/22/2025",
        "notes": "Generated plan for 25y old male"
    }
    
    print("\n📊 Creating nutrition plan...")
    print(f"Data: {json.dumps(data, indent=2)}")
    
    response = requests.post(url, json=data, headers=headers)
    
    print(f"\n📋 Response Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 201:
        print("✅ Nutrition plan created successfully!")
        plan_data = response.json()['nutrition_plan']
        print(f"Plan ID: {plan_data['id']}")
        print(f"BMR: {plan_data['bmr']}")
        print(f"TDEE: {plan_data['tdee']}")
        print(f"Target Calories: {plan_data['target_calories']}")
        print(f"Protein: {plan_data['protein_grams']}g")
        print(f"Carbs: {plan_data['carbs_grams']}g")
        print(f"Fat: {plan_data['fat_grams']}g")
        print(f"Diseases: {len(plan_data['diseases'])} selected")
    else:
        print("❌ Failed to create nutrition plan")

if __name__ == '__main__':
    test_nutrition_plan_creation()
