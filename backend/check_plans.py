#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append('/Users/mohsen/Desktop/Clinical_Nutrition_Platform/backend')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clinical_platform.settings')
django.setup()

from apps.subscriptions.models import SubscriptionPlan

def check_plans():
    """Check subscription plans and their prices"""
    
    plans = SubscriptionPlan.objects.all()
    
    if not plans.exists():
        print("No subscription plans found in database")
        return
    
    print("=== SUBSCRIPTION PLANS ===")
    for plan in plans:
        print(f"Plan: {plan.name}")
        print(f"Price: ${plan.price} {plan.currency}")
        print(f"Type: {plan.plan_type}")
        print(f"Active: {plan.is_active}")
        print(f"Stripe Price ID: {plan.stripe_price_id}")
        print(f"Features: {plan.features}")
        print("-" * 40)
    
    # Check for minimum amount issues
    print("\n=== STRIPE MINIMUM AMOUNT CHECK ===")
    for plan in plans:
        price_cents = int(float(plan.price) * 100)
        min_amount = 50  # 50 cents minimum for USD
        
        if price_cents < min_amount:
            print(f"❌ {plan.name}: ${plan.price} ({price_cents} cents) - Below minimum!")
        else:
            print(f"✅ {plan.name}: ${plan.price} ({price_cents} cents) - OK")

if __name__ == '__main__':
    check_plans()
