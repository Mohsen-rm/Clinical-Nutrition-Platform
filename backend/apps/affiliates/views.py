from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q
from .models import AffiliateCommission, AffiliateStats, PayoutRequest
from .serializers import (
    AffiliateCommissionSerializer, AffiliateStatsSerializer,
    PayoutRequestSerializer, CreatePayoutRequestSerializer
)


class AffiliateStatsView(APIView):
    def get(self, request):
        """Get affiliate statistics for the current user"""
        stats, created = AffiliateStats.objects.get_or_create(user=request.user)
        
        if created or stats.last_updated < request.user.date_joined:
            stats.update_stats()
        
        serializer = AffiliateStatsSerializer(stats)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AffiliateCommissionsView(APIView):
    def get(self, request):
        """Get commission history for the current user"""
        commissions = AffiliateCommission.objects.filter(
            affiliate=request.user
        ).select_related('referred_user', 'payment')
        
        # Filter by status if provided
        status_filter = request.query_params.get('status')
        if status_filter:
            commissions = commissions.filter(status=status_filter)
        
        # Pagination
        page_size = int(request.query_params.get('page_size', 20))
        page = int(request.query_params.get('page', 1))
        start = (page - 1) * page_size
        end = start + page_size
        
        total_count = commissions.count()
        commissions_page = commissions[start:end]
        
        serializer = AffiliateCommissionSerializer(commissions_page, many=True)
        
        return Response({
            'commissions': serializer.data,
            'total_count': total_count,
            'page': page,
            'page_size': page_size,
            'has_next': end < total_count
        }, status=status.HTTP_200_OK)


class ReferralsView(APIView):
    def get(self, request):
        """Get list of users referred by the current user"""
        from apps.accounts.serializers import UserSerializer
        
        referrals = request.user.referrals.all()
        
        # Add subscription status to each referral
        referrals_data = []
        for referral in referrals:
            user_data = UserSerializer(referral).data
            try:
                subscription = referral.subscription
                user_data['subscription_status'] = subscription.status
                user_data['subscription_active'] = subscription.is_active
            except:
                user_data['subscription_status'] = None
                user_data['subscription_active'] = False
            
            referrals_data.append(user_data)
        
        return Response({
            'referrals': referrals_data,
            'total_count': len(referrals_data)
        }, status=status.HTTP_200_OK)


class PayoutRequestsView(APIView):
    def get(self, request):
        """Get payout request history"""
        payout_requests = PayoutRequest.objects.filter(affiliate=request.user)
        serializer = PayoutRequestSerializer(payout_requests, many=True)
        
        return Response({
            'payout_requests': serializer.data
        }, status=status.HTTP_200_OK)
    
    def post(self, request):
        """Create a new payout request"""
        serializer = CreatePayoutRequestSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            # Check if user has any pending payout requests
            pending_requests = PayoutRequest.objects.filter(
                affiliate=request.user,
                status='pending'
            )
            
            if pending_requests.exists():
                return Response({
                    'error': 'You already have a pending payout request'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            payout_request = serializer.save(affiliate=request.user)
            
            return Response({
                'message': 'Payout request created successfully',
                'payout_request': PayoutRequestSerializer(payout_request).data
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def generate_referral_link(request):
    """Generate or refresh affiliate link"""
    from django.conf import settings
    
    # Generate new referral code if needed
    if not request.user.referral_code:
        import uuid
        request.user.referral_code = str(uuid.uuid4())[:8].upper()
        request.user.save()
    
    affiliate_link = f"{getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')}/register?ref={request.user.referral_code}"
    
    return Response({
        'message': 'Affiliate link generated successfully',
        'affiliate_link': affiliate_link,
        'referral_code': request.user.referral_code
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
def affiliate_dashboard(request):
    """Get comprehensive affiliate dashboard data"""
    # Get or create stats
    stats, created = AffiliateStats.objects.get_or_create(user=request.user)
    if created:
        stats.update_stats()
    
    # Get recent commissions
    recent_commissions = AffiliateCommission.objects.filter(
        affiliate=request.user
    ).select_related('referred_user', 'payment')[:5]
    
    # Get recent referrals
    recent_referrals = request.user.referrals.all()[:5]
    
    # Get pending payout requests
    pending_payouts = PayoutRequest.objects.filter(
        affiliate=request.user,
        status='pending'
    )
    
    from apps.accounts.serializers import UserSerializer
    
    from django.conf import settings
    from datetime import datetime, timedelta
    from django.db.models import Sum
    
    # Generate affiliate link
    referral_code = request.user.referral_code
    if not referral_code:
        # Generate a new referral code if user doesn't have one
        import uuid
        referral_code = str(uuid.uuid4())[:8].upper()
        request.user.referral_code = referral_code
        request.user.save()
    
    affiliate_link = f"{getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')}/register?ref={referral_code}"
    
    # Calculate monthly earnings (current month)
    current_month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    monthly_earnings = AffiliateCommission.objects.filter(
        affiliate=request.user,
        created_at__gte=current_month_start,
        status='paid'
    ).aggregate(total=Sum('commission_amount'))['total'] or 0
    
    # Available balance is total earned minus total paid
    available_balance = float(stats.total_commission_earned) - float(stats.total_commission_paid)
    
    return Response({
        'total_earnings': float(stats.total_commission_earned),
        'available_balance': available_balance,
        'total_referrals': stats.total_referrals,
        'monthly_earnings': float(monthly_earnings),
        'affiliate_link': affiliate_link,
        'referral_code': referral_code,
        'recent_commissions': AffiliateCommissionSerializer(recent_commissions, many=True).data,
        'recent_referrals': UserSerializer(recent_referrals, many=True).data,
        'recent_payouts': PayoutRequestSerializer(pending_payouts, many=True).data,
    }, status=status.HTTP_200_OK)
