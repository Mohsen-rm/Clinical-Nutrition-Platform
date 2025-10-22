from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class AffiliateCommission(models.Model):
    COMMISSION_STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('paid', _('Paid')),
        ('cancelled', _('Cancelled')),
    ]
    
    COMMISSION_TYPE_CHOICES = [
        ('subscription', _('Subscription')),
        ('one_time', _('One Time Payment')),
    ]
    
    affiliate = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='affiliate_commissions',
        help_text=_('User who will receive the commission')
    )
    referred_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='referral_commissions',
        help_text=_('User who was referred')
    )
    payment = models.ForeignKey(
        'subscriptions.Payment',
        on_delete=models.CASCADE,
        related_name='commissions',
        null=True,
        blank=True,
        help_text=_('Related payment (null for manual commissions)')
    )
    
    commission_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text=_('Commission amount in USD')
    )
    commission_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=30.00,
        help_text=_('Commission percentage (default 30%)')
    )
    commission_type = models.CharField(
        max_length=20,
        choices=COMMISSION_TYPE_CHOICES,
        default='subscription'
    )
    status = models.CharField(
        max_length=20,
        choices=COMMISSION_STATUS_CHOICES,
        default='pending'
    )
    
    paid_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'affiliates_commission'
        verbose_name = _('Affiliate Commission')
        verbose_name_plural = _('Affiliate Commissions')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Commission: {self.affiliate.email} - ${self.commission_amount}"


class AffiliateStats(models.Model):
    """Aggregated statistics for affiliates"""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='affiliate_stats'
    )
    
    total_referrals = models.PositiveIntegerField(default=0)
    active_referrals = models.PositiveIntegerField(default=0)
    total_commission_earned = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00
    )
    total_commission_paid = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00
    )
    total_commission_pending = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00
    )
    
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'affiliates_stats'
        verbose_name = _('Affiliate Statistics')
        verbose_name_plural = _('Affiliate Statistics')
    
    def __str__(self):
        return f"Stats for {self.user.email}"
    
    def update_stats(self):
        """Update affiliate statistics"""
        from apps.subscriptions.models import Subscription
        
        # Count total referrals
        self.total_referrals = self.user.referrals.count()
        
        # Count active referrals (users with active subscriptions)
        self.active_referrals = self.user.referrals.filter(
            subscription__status__in=['active', 'trialing']
        ).count()
        
        # Calculate commission totals
        commissions = self.user.affiliate_commissions.all()
        self.total_commission_earned = sum(c.commission_amount for c in commissions)
        self.total_commission_paid = sum(
            c.commission_amount for c in commissions if c.status == 'paid'
        )
        self.total_commission_pending = sum(
            c.commission_amount for c in commissions if c.status == 'pending'
        )
        
        self.save()


class PayoutRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('processing', _('Processing')),
        ('completed', _('Completed')),
        ('rejected', _('Rejected')),
    ]
    
    affiliate = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='payout_requests'
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text=_('Requested payout amount')
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    
    # Payment details
    payment_method = models.CharField(
        max_length=50,
        choices=[
            ('bank_transfer', _('Bank Transfer')),
            ('paypal', _('PayPal')),
            ('stripe', _('Stripe')),
        ],
        default='bank_transfer'
    )
    payment_details = models.JSONField(
        help_text=_('Payment method specific details (account info, etc.)')
    )
    
    processed_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True, null=True)
    admin_notes = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'affiliates_payout_request'
        verbose_name = _('Payout Request')
        verbose_name_plural = _('Payout Requests')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Payout Request: {self.affiliate.email} - ${self.amount}"
