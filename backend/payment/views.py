from django.shortcuts import render
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
import stripe
import json
import logging

from payment.models import Subscription

logger = logging.getLogger(__name__)
stripe.api_key = settings.STRIPE_SECRET_KEY

# Create your views here.

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_checkout_session(request):
    try:
        logger.info(f"Creating checkout session for user {request.user.id}")
        
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': settings.STRIPE_PREMIUM_PRICE_ID,
                'quantity': 1,
            }],
            mode='subscription',
            success_url=settings.STRIPE_SUCCESS_URL,
            cancel_url=settings.STRIPE_CANCEL_URL,
            customer_email=request.user.email,
            metadata={
                'user_id': request.user.id
            }
        )
        logger.info(f"Successfully created checkout session {checkout_session.id}")
        return Response({'checkoutUrl': checkout_session.url})
    except Exception as e:
        logger.error(f"Error creating checkout session: {str(e)}", exc_info=True)
        return Response({'error': str(e)}, status=500)

@csrf_exempt
@require_POST
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        return HttpResponse(status=400)

    # Handle the event
    if event.type == 'checkout.session.completed':
        session = event.data.object
        user_id = session.metadata.get('user_id')
        subscription_id = session.subscription

        # Update user's subscription status
        from django.contrib.auth import get_user_model
        User = get_user_model()
        try:
            user = User.objects.get(id=user_id)
            from .models import Subscription
            Subscription.objects.update_or_create(
                user=user,
                defaults={
                    'subscription_id': subscription_id,
                    'status': 'active'
                }
            )
        except User.DoesNotExist:
            return HttpResponse(status=400)

    return HttpResponse(status=200)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancel_subscription(request):
    try:
        logger.info(f"Canceling subscription for user {request.user.id}")
        
        # Get the user's subscription
        subscription = Subscription.objects.get(user=request.user)
        
        # Cancel the subscription in Stripe
        stripe.Subscription.modify(
            subscription.subscription_id,
            cancel_at_period_end=True
        )
        
        # Update our database
        subscription.status = 'canceled'
        subscription.save()
        
        logger.info(f"Successfully canceled subscription {subscription.subscription_id}")
        return Response({'message': 'Subscription will be canceled at the end of the billing period'})
    except Subscription.DoesNotExist:
        return Response({'error': 'No active subscription found'}, status=400)
    except Exception as e:
        logger.error(f"Error canceling subscription: {str(e)}", exc_info=True)
        return Response({'error': str(e)}, status=500)
