#!/usr/bin/env python
import os
import sys
import django
import uuid

# Add the project directory to the Python path
sys.path.append('/Users/mohsen/Desktop/Clinical_Nutrition_Platform/backend')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clinical_platform.settings')
django.setup()

from apps.accounts.models import User

def generate_referral_codes():
    """Generate referral codes for users who don't have them"""
    users_without_codes = User.objects.filter(referral_code__isnull=True) | User.objects.filter(referral_code='')
    
    print(f"Found {users_without_codes.count()} users without referral codes")
    
    for user in users_without_codes:
        # Generate unique referral code
        while True:
            code = str(uuid.uuid4())[:8].upper()
            if not User.objects.filter(referral_code=code).exists():
                break
        
        user.referral_code = code
        user.save()
        print(f"Generated referral code '{code}' for user: {user.email}")
    
    print("All users now have referral codes!")

if __name__ == '__main__':
    generate_referral_codes()
