#!/usr/bin/env python
"""
Sample data creation script for Clinical Nutrition Platform
Run this after migrations to populate the database with sample data
"""
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clinical_platform.settings')
django.setup()

from apps.accounts.models import User
from apps.subscriptions.models import SubscriptionPlan
from apps.nutrition.models import Disease
from django.contrib.auth import get_user_model

def create_sample_data():
    print("Creating sample data...")
    
    # Create subscription plans
    plans_data = [
        {
            'name': 'Basic Plan',
            'description': 'Perfect for individual practitioners',
            'price': 29.00,
            'plan_type': 'basic',
            'stripe_price_id': 'price_basic_test',
            'stripe_product_id': 'prod_basic_test',
            'features': [
                'Basic nutrition planning',
                'Up to 50 patients',
                'Email support',
                'Mobile app access'
            ]
        },
        {
            'name': 'Professional Plan',
            'description': 'Advanced features for growing practices',
            'price': 79.00,
            'plan_type': 'premium',
            'stripe_price_id': 'price_pro_test',
            'stripe_product_id': 'prod_pro_test',
            'features': [
                'Advanced nutrition planning',
                'Unlimited patients',
                'WhatsApp integration',
                'Disease-specific calculations',
                'Priority support',
                'Analytics dashboard'
            ]
        },
        {
            'name': 'Enterprise Plan',
            'description': 'Complete solution for large clinics',
            'price': 149.00,
            'plan_type': 'professional',
            'stripe_price_id': 'price_ent_test',
            'stripe_product_id': 'prod_ent_test',
            'features': [
                'Everything in Professional',
                'Multi-clinic support',
                'API access',
                'Custom integrations',
                'Dedicated support',
                'White-label options'
            ]
        }
    ]
    
    for plan_data in plans_data:
        plan, created = SubscriptionPlan.objects.get_or_create(
            name=plan_data['name'],
            defaults=plan_data
        )
        if created:
            print(f"Created subscription plan: {plan.name}")
    
    # Create diseases
    diseases_data = [
        {
            'name': 'Diabetes Type 2',
            'description': 'A chronic condition affecting blood sugar regulation',
            'dietary_restrictions': 'Low carbohydrate, controlled portions, regular meal timing',
            'calorie_adjustment': -200
        },
        {
            'name': 'Hyperthyroidism',
            'description': 'Overactive thyroid gland causing increased metabolism',
            'dietary_restrictions': 'High calorie, increased protein, avoid caffeine',
            'calorie_adjustment': 300
        },
        {
            'name': 'Hypertension',
            'description': 'High blood pressure requiring dietary management',
            'dietary_restrictions': 'Low sodium, DASH diet, limited processed foods',
            'calorie_adjustment': -100
        },
        {
            'name': 'Hypothyroidism',
            'description': 'Underactive thyroid gland causing slower metabolism',
            'dietary_restrictions': 'Moderate calorie restriction, avoid goitrogens',
            'calorie_adjustment': -150
        },
        {
            'name': 'Cardiovascular Disease',
            'description': 'Heart and blood vessel conditions',
            'dietary_restrictions': 'Low saturated fat, high fiber, omega-3 rich foods',
            'calorie_adjustment': -100
        },
        {
            'name': 'Chronic Kidney Disease',
            'description': 'Progressive loss of kidney function',
            'dietary_restrictions': 'Protein restriction, phosphorus control, potassium management',
            'calorie_adjustment': -50
        }
    ]
    
    for disease_data in diseases_data:
        disease, created = Disease.objects.get_or_create(
            name=disease_data['name'],
            defaults=disease_data
        )
        if created:
            print(f"Created disease: {disease.name}")
    
    # Create sample users
    User = get_user_model()
    
    # Create admin user
    if not User.objects.filter(email='admin@example.com').exists():
        admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123',
            first_name='Admin',
            last_name='User',
            user_type='doctor'
        )
        print(f"Created admin user: {admin_user.email}")
    
    # Create sample doctor
    if not User.objects.filter(email='doctor@example.com').exists():
        doctor = User.objects.create_user(
            username='doctor1',
            email='doctor@example.com',
            password='doctor123',
            first_name='Dr. Sarah',
            last_name='Johnson',
            user_type='doctor',
            is_verified=True
        )
        print(f"Created doctor user: {doctor.email}")
    
    # Create sample patient
    if not User.objects.filter(email='patient@example.com').exists():
        patient = User.objects.create_user(
            username='patient1',
            email='patient@example.com',
            password='patient123',
            first_name='John',
            last_name='Doe',
            user_type='patient',
            is_verified=True
        )
        print(f"Created patient user: {patient.email}")
    
    print("Sample data creation completed!")

if __name__ == '__main__':
    create_sample_data()
