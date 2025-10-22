#!/usr/bin/env python
import os
import sys
import django
from decimal import Decimal

# Add the project directory to the Python path
sys.path.append('/Users/mohsen/Desktop/Clinical_Nutrition_Platform/backend')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clinical_platform.settings')
django.setup()

from apps.accounts.models import User
from apps.affiliates.models import AffiliateStats, AffiliateCommission
from apps.subscriptions.models import Payment, Subscription

def create_sample_data():
    """Create sample affiliate data for testing"""
    
    # Get users
    try:
        admin = User.objects.get(email='admin@example.com')
        doctor = User.objects.get(email='doctor@example.com')
        patient = User.objects.get(email='patient@example.com')
    except User.DoesNotExist:
        print("Users not found. Please make sure test users exist.")
        return
    
    # Create or update affiliate stats for admin
    admin_stats, created = AffiliateStats.objects.get_or_create(user=admin)
    admin_stats.total_referrals = 2
    admin_stats.active_referrals = 1
    admin_stats.total_commission_earned = Decimal('150.00')
    admin_stats.total_commission_paid = Decimal('50.00')
    admin_stats.total_commission_pending = Decimal('100.00')
    admin_stats.save()
    
    print(f"Created/Updated affiliate stats for admin: {admin_stats}")
    
    # Create or update affiliate stats for doctor
    doctor_stats, created = AffiliateStats.objects.get_or_create(user=doctor)
    doctor_stats.total_referrals = 1
    doctor_stats.active_referrals = 1
    doctor_stats.total_commission_earned = Decimal('87.00')
    doctor_stats.total_commission_paid = Decimal('0.00')
    doctor_stats.total_commission_pending = Decimal('87.00')
    doctor_stats.save()
    
    print(f"Created/Updated affiliate stats for doctor: {doctor_stats}")
    
    # Create or update affiliate stats for patient
    patient_stats, created = AffiliateStats.objects.get_or_create(user=patient)
    patient_stats.total_referrals = 0
    patient_stats.active_referrals = 0
    patient_stats.total_commission_earned = Decimal('0.00')
    patient_stats.total_commission_paid = Decimal('0.00')
    patient_stats.total_commission_pending = Decimal('0.00')
    patient_stats.save()
    
    print(f"Created/Updated affiliate stats for patient: {patient_stats}")
    
    print("\nSample affiliate data created successfully!")
    print("Now you can test the affiliate dashboard.")

if __name__ == '__main__':
    create_sample_data()
