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

def test_plan_details():
    """Test nutrition plan details API"""
    
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
    
    if 'tokens' in login_data and 'access' in login_data['tokens']:
        token = login_data['tokens']['access']
    else:
        print(f"❌ No access token found in response")
        return
        
    print(f"✅ Login successful")
    
    # Test getting plan details
    plan_id = 1  # Assuming we have a plan with ID 1
    url = f'http://localhost:8000/api/nutrition/plans/{plan_id}/'
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    print(f"\n📊 Getting plan details for ID {plan_id}...")
    
    response = requests.get(url, headers=headers)
    
    print(f"\n📋 Response Status: {response.status_code}")
    
    if response.status_code == 200:
        plan_data = response.json()
        print("✅ Plan details retrieved successfully!")
        print(f"Response structure: {json.dumps(plan_data, indent=2)}")
        
        if 'nutrition_plan' in plan_data:
            plan = plan_data['nutrition_plan']
            print(f"\n📋 Plan Details:")
            print(f"  - ID: {plan.get('id')}")
            print(f"  - Name: {plan.get('name')}")
            print(f"  - Age: {plan.get('age')}")
            print(f"  - Target Calories: {plan.get('target_calories')}")
            print(f"  - Diseases: {len(plan.get('diseases', []))}")
        
    elif response.status_code == 404:
        print("❌ Plan not found - this is expected if no plans exist yet")
        print("Create a plan first using the nutrition calculator")
    elif response.status_code == 403:
        print("❌ Permission denied - user doesn't have access to this plan")
    else:
        print(f"❌ Failed to get plan details: {response.status_code}")
        print(response.text)

if __name__ == '__main__':
    test_plan_details()
