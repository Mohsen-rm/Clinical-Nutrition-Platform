from django.urls import path
from .views import (
    AffiliateStatsView, AffiliateCommissionsView, ReferralsView,
    PayoutRequestsView, generate_referral_link, affiliate_dashboard
)

urlpatterns = [
    path('stats/', AffiliateStatsView.as_view(), name='affiliate_stats'),
    path('commissions/', AffiliateCommissionsView.as_view(), name='affiliate_commissions'),
    path('referrals/', ReferralsView.as_view(), name='affiliate_referrals'),
    path('payouts/', PayoutRequestsView.as_view(), name='payout_requests'),
    path('generate-link/', generate_referral_link, name='generate_referral_link'),
    path('dashboard/', affiliate_dashboard, name='affiliate_dashboard'),
]
