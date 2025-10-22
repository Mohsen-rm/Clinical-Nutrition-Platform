#!/usr/bin/env python
"""
Test script to test subscription creation via API
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clinical_platform.settings')
django.setup()

import stripe
from django.conf import settings
from django.contrib.auth import get_user_model
from apps.subscriptions.models import SubscriptionPlan
from apps.subscriptions.stripe_service import StripeService

User = get_user_model()

# Configure Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

def test_subscription_api():
    """Test subscription creation through StripeService"""
    
    print("🧪 Testing subscription creation via StripeService...")
    
    try:
        # Get or create test user
        user, created = User.objects.get_or_create(
            email='test@example.com',
            defaults={
                'first_name': 'Test',
                'last_name': 'User',
                'user_type': 'patient'
            }
        )
        if created:
            user.set_password('testpass123')
            user.save()
        
        print(f"✅ Test user: {user.email} (ID: {user.id})")
        
        # Get Basic Plan
        plan = SubscriptionPlan.objects.get(plan_type='basic')
        print(f"✅ Plan: {plan.name} (ID: {plan.id})")
        
        # Create test payment method using Stripe test token
        payment_method = stripe.PaymentMethod.create(
            type='card',
            card={'token': 'tok_visa'},
        )
        print(f"✅ Payment method created: {payment_method.id}")
        
        # Test subscription creation
        result = StripeService.create_subscription(
            user=user,
            plan_id=plan.id,
            payment_method_id=payment_method.id
        )
        
        print(f"🎉 Subscription created successfully!")
        print(f"   Database ID: {result['subscription'].id}")
        print(f"   Stripe ID: {result['subscription_id']}")
        print(f"   Status: {result['subscription'].status}")
        
        # Clean up
        result['subscription'].delete()
        stripe.Subscription.delete(result['subscription_id'])
        print(f"✅ Cleaned up test data")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_subscription_api()
