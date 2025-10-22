#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append('/Users/mohsen/Desktop/Clinical_Nutrition_Platform/backend')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clinical_platform.settings')
django.setup()

from apps.accounts.serializers import UserRegistrationSerializer

def test_registration():
    """Test user registration with referral code"""
    
    data = {
        'first_name': 'Test',
        'last_name': 'User',
        'email': 'testuser3@example.com',
        'password': 'TestPass123!',
        'password_confirm': 'TestPass123!',
        'user_type': 'patient',
        'referral_code': '36C93C3D'  # Patient's referral code
    }
    
    serializer = UserRegistrationSerializer(data=data)
    
    if serializer.is_valid():
        user = serializer.save()
        print(f"✅ User created successfully!")
        print(f"Username: {user.username}")
        print(f"Email: {user.email}")
        print(f"Referral Code: {user.referral_code}")
        print(f"Referred By: {user.referred_by}")
        return True
    else:
        print("❌ Registration failed!")
        print("Errors:", serializer.errors)
        return False

if __name__ == '__main__':
    test_registration()
