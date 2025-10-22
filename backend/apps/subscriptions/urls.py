from django.urls import path
from .views import (
    SubscriptionPlansView, CreateSubscriptionView, SubscriptionStatusView,
    CancelSubscriptionView, create_payment_intent, stripe_webhook
)

urlpatterns = [
    path('plans/', SubscriptionPlansView.as_view(), name='subscription_plans'),
    path('create/', CreateSubscriptionView.as_view(), name='create_subscription'),
    path('status/', SubscriptionStatusView.as_view(), name='subscription_status'),
    path('cancel/', CancelSubscriptionView.as_view(), name='cancel_subscription'),
    path('payment-intent/', create_payment_intent, name='create_payment_intent'),
    path('webhook/', stripe_webhook, name='stripe_webhook'),
]
