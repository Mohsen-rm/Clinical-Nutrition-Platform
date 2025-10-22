from rest_framework import serializers
from .models import AffiliateCommission, AffiliateStats, PayoutRequest
from apps.accounts.serializers import UserSerializer


class AffiliateCommissionSerializer(serializers.ModelSerializer):
    referred_user = UserSerializer(read_only=True)
    
    class Meta:
        model = AffiliateCommission
        fields = [
            'id', 'referred_user', 'commission_amount', 'commission_percentage',
            'commission_type', 'status', 'paid_at', 'created_at'
        ]


class AffiliateStatsSerializer(serializers.ModelSerializer):
    referral_link = serializers.SerializerMethodField()
    
    class Meta:
        model = AffiliateStats
        fields = [
            'total_referrals', 'active_referrals', 'total_commission_earned',
            'total_commission_paid', 'total_commission_pending',
            'last_updated', 'referral_link'
        ]
    
    def get_referral_link(self, obj):
        from django.conf import settings
        frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
        return f"{frontend_url}/register?ref={obj.user.referral_code}"


class PayoutRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = PayoutRequest
        fields = [
            'id', 'amount', 'status', 'payment_method', 'payment_details',
            'processed_at', 'rejection_reason', 'created_at'
        ]
        read_only_fields = ['status', 'processed_at', 'rejection_reason']


class CreatePayoutRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = PayoutRequest
        fields = ['amount', 'payment_method', 'payment_details']
    
    def validate_amount(self, value):
        user = self.context['request'].user
        try:
            stats = user.affiliate_stats
            if value > stats.total_commission_pending:
                raise serializers.ValidationError(
                    f"Requested amount exceeds available balance of ${stats.total_commission_pending}"
                )
        except AffiliateStats.DoesNotExist:
            raise serializers.ValidationError("No affiliate statistics found")
        
        if value < 10:  # Minimum payout amount
            raise serializers.ValidationError("Minimum payout amount is $10")
        
        return value
    
    def validate_payment_details(self, value):
        payment_method = self.initial_data.get('payment_method')
        
        if payment_method == 'bank_transfer':
            required_fields = ['account_number', 'routing_number', 'account_holder_name']
        elif payment_method == 'paypal':
            required_fields = ['paypal_email']
        elif payment_method == 'stripe':
            required_fields = ['stripe_account_id']
        else:
            raise serializers.ValidationError("Invalid payment method")
        
        for field in required_fields:
            if field not in value:
                raise serializers.ValidationError(f"Missing required field: {field}")
        
        return value
