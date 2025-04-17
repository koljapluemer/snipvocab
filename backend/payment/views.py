from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
import stripe
import logging

from payment.models import StripeCustomer

logger = logging.getLogger(__name__)
stripe.api_key = settings.STRIPE_SECRET_KEY

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_checkout_session(request):
    try:
        logger.info(f"Creating checkout session for user {request.user.id}")
        
        # Create or get Stripe customer
        try:
            stripe_customer = StripeCustomer.objects.get(user=request.user)
            customer_id = stripe_customer.customer_id
        except StripeCustomer.DoesNotExist:
            customer = stripe.Customer.create(email=request.user.email)
            stripe_customer = StripeCustomer.objects.create(
                user=request.user,
                customer_id=customer.id
            )
            customer_id = customer.id

        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': settings.STRIPE_PREMIUM_PRICE_ID,
                'quantity': 1,
            }],
            mode='subscription',
            success_url=settings.STRIPE_SUCCESS_URL,
            cancel_url=settings.STRIPE_CANCEL_URL,
            customer=customer_id,
            metadata={
                'user_id': request.user.id
            }
        )
        logger.info(f"Successfully created checkout session {checkout_session.id}")
        return Response({'checkoutUrl': checkout_session.url})
    except Exception as e:
        logger.error(f"Error creating checkout session: {str(e)}", exc_info=True)
        return Response({'error': str(e)}, status=500)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_customer_portal_session(request):
    try:
        stripe_customer = StripeCustomer.objects.get(user=request.user)
        session = stripe.billing_portal.Session.create(
            customer=stripe_customer.customer_id,
            return_url=settings.STRIPE_SUCCESS_URL,
        )
        return Response({'portalUrl': session.url})
    except StripeCustomer.DoesNotExist:
        return Response({'error': 'No Stripe customer found'}, status=400)
    except Exception as e:
        logger.error(f"Error creating customer portal session: {str(e)}", exc_info=True)
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
        customer_id = session.customer

        # Update user's Stripe customer ID if needed
        from django.contrib.auth import get_user_model
        User = get_user_model()
        try:
            user = User.objects.get(id=user_id)
            StripeCustomer.objects.update_or_create(
                user=user,
                defaults={'customer_id': customer_id}
            )
        except User.DoesNotExist:
            return HttpResponse(status=400)

    return HttpResponse(status=200)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_subscription_info(request):
    try:
        stripe_customer = StripeCustomer.objects.get(user=request.user)
        
        # Get the customer's subscriptions
        subscriptions = stripe.Subscription.list(
            customer=stripe_customer.customer_id,
            status='all',
            limit=1
        )
        
        if not subscriptions.data:
            return Response({'subscription': None})
            
        subscription = subscriptions.data[0]
        
        # Get the current period end from the first subscription item
        current_period_end = None
        if subscription.get('items', {}).get('data'):
            current_period_end = subscription['items']['data'][0]['current_period_end']
        
        subscription_details = {
            'status': subscription.status,
            'period_end': current_period_end,
            'cancel_at': subscription.get('cancel_at'),
            'cancel_at_period_end': subscription.get('cancel_at_period_end', False)
        }
        
        return Response({'subscription': subscription_details})
    except StripeCustomer.DoesNotExist:
        # User has no Stripe customer record yet, which is fine
        return Response({'subscription': None})
    except stripe.error.StripeError as e:
        # Only log and return error for actual Stripe API errors
        logger.error(f"Error fetching Stripe subscription: {str(e)}", exc_info=True)
        return Response({
            'subscription': {
                'error': 'Failed to fetch subscription details'
            }
        }, status=500)
