from rest_framework import serializers
from .models import SubscriptionPlan, Subscription, Payment


class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = [
            'id', 'name', 'description', 'price', 'currency',
            'plan_type', 'features', 'is_active'
        ]


class SubscriptionSerializer(serializers.ModelSerializer):
    plan = SubscriptionPlanSerializer(read_only=True)
    plan_id = serializers.ReadOnlyField(source='plan.id')
    plan_name = serializers.ReadOnlyField(source='plan.name')
    amount = serializers.SerializerMethodField()
    days_until_renewal = serializers.ReadOnlyField()
    is_active = serializers.ReadOnlyField()
    
    class Meta:
        model = Subscription
        fields = [
            'id', 'plan', 'plan_id', 'plan_name', 'amount', 'status', 
            'current_period_start', 'current_period_end', 'cancel_at_period_end',
            'canceled_at', 'days_until_renewal', 'is_active', 'created_at'
        ]
    
    def get_amount(self, obj):
        """Return amount in cents for frontend compatibility"""
        return int(float(obj.plan.price) * 100)


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            'id', 'amount', 'currency', 'status',
            'affiliate_commission', 'affiliate_paid',
            'created_at'
        ]


class CreateSubscriptionSerializer(serializers.Serializer):
    plan_id = serializers.IntegerField()
    payment_method_id = serializers.CharField(max_length=100)
    
    def validate_plan_id(self, value):
        try:
            plan = SubscriptionPlan.objects.get(id=value, is_active=True)
            return value
        except SubscriptionPlan.DoesNotExist:
            raise serializers.ValidationError("Invalid or inactive plan selected.")


class CancelSubscriptionSerializer(serializers.Serializer):
    cancel_at_period_end = serializers.BooleanField(default=True)
