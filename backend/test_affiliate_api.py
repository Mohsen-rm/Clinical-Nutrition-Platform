#!/usr/bin/env python
"""
Direct test of the affiliate API
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clinical_platform.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.test import RequestFactory
from apps.affiliates.views import affiliate_dashboard
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

def test_affiliate_dashboard():
    """Test affiliate dashboard API"""
    print('🧪 Testing affiliate dashboard API:')
    print('=' * 40)
    
    try:
        # Get user doctor@example.com
        user = User.objects.get(email='doctor@example.com')
        print(f'✅ User found: {user.email}')
        
        # Create a fake request
        factory = RequestFactory()
        request = factory.get('/api/affiliates/dashboard/')
        request.user = user
        
        # Call the view
        response = affiliate_dashboard(request)
        
        print(f'📊 Response status: {response.status_code}')
        
        if response.status_code == 200:
            data = response.data
            print(f'✅ Received data:')
            print(f'   Total Earnings: ${data.get("total_earnings", 0)}')
            print(f'   Available Balance: ${data.get("available_balance", 0)}')
            print(f'   Total Referrals: {data.get("total_referrals", 0)}')
            print(f'   Monthly Earnings: ${data.get("monthly_earnings", 0)}')
            print(f'   Affiliate Link: {data.get("affiliate_link", "N/A")}')
            print(f'   Referral Code: {data.get("referral_code", "N/A")}')
            
            # Recent commissions
            recent_commissions = data.get('recent_commissions', [])
            print(f'\n💰 Recent commissions ({len(recent_commissions)}):')
            for commission in recent_commissions:
                print(f'   ${commission.get("commission_amount")} - {commission.get("status")}')
            
            # Recent referrals
            recent_referrals = data.get('recent_referrals', [])
            print(f'\n👥 Recent referrals ({len(recent_referrals)}):')
            for referral in recent_referrals:
                print(f'   {referral.get("email")} - {referral.get("user_type")}')
                
        else:
            print(f'❌ Response error: {response.status_code}')
            if hasattr(response, 'data'):
                print(f'   Details: {response.data}')
                
    except User.DoesNotExist:
        print('❌ User doctor@example.com does not exist')
    except Exception as e:
        print(f'❌ Error: {str(e)}')

def test_commission_api():
    """Test commissions API"""
    print('\n🧪 Testing commissions API:')
    print('=' * 30)
    
    try:
        user = User.objects.get(email='doctor@example.com')
        
        from apps.affiliates.views import AffiliateCommissionsView
        
        factory = RequestFactory()
        request = factory.get('/api/affiliates/commissions/')
        request.user = user
        request.query_params = {}
        
        view = AffiliateCommissionsView()
        response = view.get(request)
        
        print(f'📊 Response status: {response.status_code}')
        
        if response.status_code == 200:
            data = response.data
            commissions = data.get('commissions', [])
            total_count = data.get('total_count', 0)
            
            print(f'✅ Total commissions: {total_count}')
            print(f'✅ Commissions on page: {len(commissions)}')
            
            for commission in commissions:
                print(f'   ${commission.get("commission_amount")} - {commission.get("status")} - {commission.get("created_at", "")[:10]}')
        else:
            print(f'❌ Response error: {response.status_code}')
            
    except Exception as e:
        print(f'❌ Error: {str(e)}')

def main():
    """Main function"""
    print('🚀 Testing affiliate APIs')
    print('=' * 30)
    
    test_affiliate_dashboard()
    test_commission_api()
    
    print('\n📋 Summary:')
    print('If all tests passed, the affiliate dashboard should show:')
    print('- Total Earnings: $47.40')
    print('- Available Balance: $32.40') 
    print('- Total Referrals: 2')
    print('- Recent commissions from test1 and test2')

if __name__ == '__main__':
    main()
