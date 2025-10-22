from django.contrib import admin
from django.utils import timezone
from .models import AffiliateCommission, AffiliateStats, PayoutRequest


@admin.register(AffiliateCommission)
class AffiliateCommissionAdmin(admin.ModelAdmin):
    list_display = ('affiliate_email', 'referred_user_email', 'commission_amount', 'status', 'commission_type', 'created_at')
    list_filter = ('status', 'commission_type', 'created_at')
    search_fields = ('affiliate__email', 'referred_user__email')
    readonly_fields = ('created_at', 'updated_at')
    actions = ['mark_as_paid', 'mark_as_cancelled']
    
    def affiliate_email(self, obj):
        return obj.affiliate.email
    affiliate_email.short_description = 'Affiliate'
    
    def referred_user_email(self, obj):
        return obj.referred_user.email
    referred_user_email.short_description = 'Referred User'
    
    def mark_as_paid(self, request, queryset):
        updated = queryset.update(status='paid', paid_at=timezone.now())
        self.message_user(request, f'{updated} commissions marked as paid.')
    mark_as_paid.short_description = 'Mark selected commissions as paid'
    
    def mark_as_cancelled(self, request, queryset):
        updated = queryset.update(status='cancelled')
        self.message_user(request, f'{updated} commissions marked as cancelled.')
    mark_as_cancelled.short_description = 'Mark selected commissions as cancelled'


@admin.register(AffiliateStats)
class AffiliateStatsAdmin(admin.ModelAdmin):
    list_display = ('user_email', 'total_referrals', 'active_referrals', 'total_commission_earned', 'total_commission_pending', 'last_updated')
    search_fields = ('user__email', 'user__first_name', 'user__last_name')
    readonly_fields = ('last_updated',)
    actions = ['update_stats']
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'User'
    
    def update_stats(self, request, queryset):
        for stats in queryset:
            stats.update_stats()
        self.message_user(request, f'{queryset.count()} affiliate stats updated.')
    update_stats.short_description = 'Update selected affiliate statistics'


@admin.register(PayoutRequest)
class PayoutRequestAdmin(admin.ModelAdmin):
    list_display = ('affiliate_email', 'amount', 'status', 'payment_method', 'created_at', 'processed_at')
    list_filter = ('status', 'payment_method', 'created_at')
    search_fields = ('affiliate__email',)
    readonly_fields = ('created_at', 'updated_at')
    actions = ['approve_payout', 'reject_payout']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('affiliate', 'amount', 'status', 'payment_method')
        }),
        ('Payment Details', {
            'fields': ('payment_details',)
        }),
        ('Processing Information', {
            'fields': ('processed_at', 'rejection_reason', 'admin_notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def affiliate_email(self, obj):
        return obj.affiliate.email
    affiliate_email.short_description = 'Affiliate'
    
    def approve_payout(self, request, queryset):
        updated = queryset.filter(status='pending').update(
            status='completed',
            processed_at=timezone.now()
        )
        self.message_user(request, f'{updated} payout requests approved.')
    approve_payout.short_description = 'Approve selected payout requests'
    
    def reject_payout(self, request, queryset):
        updated = queryset.filter(status='pending').update(
            status='rejected',
            processed_at=timezone.now()
        )
        self.message_user(request, f'{updated} payout requests rejected.')
    reject_payout.short_description = 'Reject selected payout requests'
