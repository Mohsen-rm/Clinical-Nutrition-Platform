#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append('/Users/mohsen/Desktop/Clinical_Nutrition_Platform/backend')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clinical_platform.settings')
django.setup()

try:
    from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
    
    # Clear all blacklisted tokens
    blacklisted_count = BlacklistedToken.objects.count()
    outstanding_count = OutstandingToken.objects.count()
    
    BlacklistedToken.objects.all().delete()
    OutstandingToken.objects.all().delete()
    
    print(f"Cleared {blacklisted_count} blacklisted tokens")
    print(f"Cleared {outstanding_count} outstanding tokens")
    print("All tokens cleared successfully!")
    
except ImportError:
    print("Token blacklist not installed - no tokens to clear")
except Exception as e:
    print(f"Error clearing tokens: {e}")
