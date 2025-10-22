from django.contrib import admin
from .models import SubscriptionPlan, Subscription, Payment, WebhookEvent


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'plan_type', 'price', 'currency', 'is_active', 'created_at')
    list_filter = ('plan_type', 'is_active', 'currency')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan', 'status', 'current_period_end', 'cancel_at_period_end', 'created_at')
    list_filter = ('status', 'cancel_at_period_end', 'plan__plan_type')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'stripe_subscription_id')
    readonly_fields = ('stripe_subscription_id', 'stripe_customer_id', 'created_at', 'updated_at')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'plan')


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('subscription_user', 'amount', 'currency', 'status', 'affiliate_commission', 'affiliate_paid', 'created_at')
    list_filter = ('status', 'currency', 'affiliate_paid')
    search_fields = ('subscription__user__email', 'stripe_payment_intent_id')
    readonly_fields = ('stripe_payment_intent_id', 'created_at', 'updated_at')
    
    def subscription_user(self, obj):
        return obj.subscription.user.email
    subscription_user.short_description = 'User'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('subscription__user')


@admin.register(WebhookEvent)
class WebhookEventAdmin(admin.ModelAdmin):
    list_display = ('stripe_event_id', 'event_type', 'processed', 'created_at')
    list_filter = ('event_type', 'processed')
    search_fields = ('stripe_event_id', 'event_type')
    readonly_fields = ('stripe_event_id', 'event_type', 'data', 'created_at')
