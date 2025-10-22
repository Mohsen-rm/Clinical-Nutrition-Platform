import stripe
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
import json

from .models import SubscriptionPlan, Subscription, WebhookEvent
from .serializers import (
    SubscriptionPlanSerializer, SubscriptionSerializer,
    CreateSubscriptionSerializer, CancelSubscriptionSerializer
)
from .stripe_service import StripeService

stripe.api_key = settings.STRIPE_SECRET_KEY


class SubscriptionPlansView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        plans = SubscriptionPlan.objects.filter(is_active=True)
        serializer = SubscriptionPlanSerializer(plans, many=True)
        return Response({
            'plans': serializer.data
        }, status=status.HTTP_200_OK)


class CreateSubscriptionView(APIView):
    def post(self, request):
        print(f"Create subscription request data: {request.data}")  # Debug log
        
        serializer = CreateSubscriptionSerializer(data=request.data)
        if serializer.is_valid():
            try:
                # Check if user already has an active subscription
                if hasattr(request.user, 'subscription') and request.user.subscription.is_active:
                    return Response({
                        'error': 'User already has an active subscription'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                result = StripeService.create_subscription(
                    user=request.user,
                    plan_id=serializer.validated_data['plan_id'],
                    payment_method_id=serializer.validated_data['payment_method_id']
                )
                
                return Response({
                    'message': 'Subscription created successfully',
                    'subscription': SubscriptionSerializer(result['subscription']).data,
                    'client_secret': result['client_secret']
                }, status=status.HTTP_201_CREATED)
                
            except Exception as e:
                print(f"Subscription creation error: {str(e)}")  # Debug log
                return Response({
                    'error': str(e)
                }, status=status.HTTP_400_BAD_REQUEST)
        
        print(f"Serializer errors: {serializer.errors}")  # Debug log
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SubscriptionStatusView(APIView):
    def get(self, request):
        try:
            subscription = request.user.subscription
            return Response({
                'subscription': SubscriptionSerializer(subscription).data
            }, status=status.HTTP_200_OK)
        except Subscription.DoesNotExist:
            return Response({
                'subscription': None,
                'message': 'No active subscription found'
            }, status=status.HTTP_200_OK)


class CancelSubscriptionView(APIView):
    def post(self, request):
        try:
            subscription = request.user.subscription
            serializer = CancelSubscriptionSerializer(data=request.data)
            
            if serializer.is_valid():
                cancel_at_period_end = serializer.validated_data.get('cancel_at_period_end', True)
                
                updated_subscription = StripeService.cancel_subscription(
                    subscription.stripe_subscription_id,
                    cancel_at_period_end
                )
                
                return Response({
                    'message': 'Subscription canceled successfully',
                    'subscription': SubscriptionSerializer(updated_subscription).data
                }, status=status.HTTP_200_OK)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except Subscription.DoesNotExist:
            return Response({
                'error': 'No active subscription found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def create_payment_intent(request):
    """Create a payment intent for subscription payments"""
    try:
        plan_id = request.data.get('plan_id')
        if not plan_id:
            return Response({
                'error': 'plan_id is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get the subscription plan
        try:
            plan = SubscriptionPlan.objects.get(id=plan_id, is_active=True)
        except SubscriptionPlan.DoesNotExist:
            return Response({
                'error': 'Invalid subscription plan'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Calculate amount in cents
        amount = int(float(plan.price) * 100)
        currency = plan.currency.lower()
        
        # Create payment intent
        intent = stripe.PaymentIntent.create(
            amount=amount,
            currency=currency,
            metadata={
                'user_id': request.user.id,
                'plan_id': plan.id,
                'plan_name': plan.name
            }
        )
        
        return Response({
            'client_secret': intent.client_secret,
            'amount': amount,
            'currency': currency
        }, status=status.HTTP_200_OK)
        
    except stripe.StripeError as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
@require_POST
def stripe_webhook(request):
    """Handle Stripe webhook events"""
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)
    
    # Check if we've already processed this event
    webhook_event, created = WebhookEvent.objects.get_or_create(
        stripe_event_id=event['id'],
        defaults={
            'event_type': event['type'],
            'data': event['data'],
            'processed': False
        }
    )
    
    if not created and webhook_event.processed:
        return HttpResponse(status=200)
    
    # Process the event
    try:
        StripeService.handle_webhook_event(event)
        webhook_event.processed = True
        webhook_event.save()
    except Exception as e:
        print(f"Error processing webhook: {str(e)}")
        return HttpResponse(status=500)
    
    return HttpResponse(status=200)
