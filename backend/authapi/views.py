from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings
from .forms import CreateUserForm
from django.contrib.auth import get_user_model
import logging
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.exceptions import AuthenticationFailed
import stripe

logger = logging.getLogger(__name__)
User = get_user_model()

class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        
        # Get the user from the request data
        email = request.data.get('username')  # JWT uses username field for email
        try:
            user = User.objects.get(email=email)
            if not user.is_active:
                raise AuthenticationFailed('Please confirm your email before logging in.')
        except User.DoesNotExist:
            pass  # Let the parent class handle invalid credentials
        
        return response

# Create your views here.

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    form = CreateUserForm(request.data)
    if form.is_valid():
        user = form.save()
        refresh = RefreshToken.for_user(user)
        
        # Generate confirmation token and URL
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        confirm_url = f"{settings.FRONTEND_PASSWORD_RESET_URL}/confirm-email?uid={uid}&token={token}"
        
        # Send confirmation email
        subject = 'Welcome to SnipVocab - Confirm your email'
        message = f'Thanks for registering! Click this link to confirm your email: {confirm_url}'
        from_email = settings.DEFAULT_FROM_EMAIL
        
        try:
            logger.info(f"Sending welcome email to {user.email}")
            send_mail(subject, message, from_email, [user.email])
            logger.info("Welcome email sent successfully")
        except Exception as e:
            logger.error(f"Failed to send welcome email: {str(e)}", exc_info=True)
            # Still create the user, but log the error
        
        return Response({
            'message': 'Registration successful. A welcome email has been sent.',
            'user_id': user.id,
            'email': user.email,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)
    return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def confirm_email(request):
    uid = request.data.get('uid')
    token = request.data.get('token')
    
    try:
        uid = force_str(urlsafe_base64_decode(uid))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return Response({'error': 'Invalid confirmation link'}, 
                       status=status.HTTP_400_BAD_REQUEST)
    
    if not default_token_generator.check_token(user, token):
        return Response({'error': 'Invalid confirmation link'}, 
                       status=status.HTTP_400_BAD_REQUEST)
    
    return Response({'message': 'Email confirmed successfully'}, 
                   status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    # With JWT, we don't need to do anything on the server side
    # The client should simply discard the tokens
    return Response({'message': 'Logout successful'})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_info(request):
    return Response({
        'email': request.user.email,
        'id': request.user.id
    })

@api_view(['POST'])
@permission_classes([AllowAny])
def request_password_reset(request):
    email = request.data.get('email')
    logger.info(f"Password reset requested for email: {email}")
    
    try:
        user = User.objects.get(email=email)
        logger.info(f"User found for email: {email}")
    except User.DoesNotExist:
        logger.info(f"No user found for email: {email}")
        return Response({'message': 'If an account exists with this email, a password reset link has been sent.'}, 
                       status=status.HTTP_200_OK)

    # Generate token and uid
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    
    # Create reset URL
    reset_url = f"{settings.FRONTEND_PASSWORD_RESET_URL}?uid={uid}&token={token}"
    logger.info(f"Generated reset URL: {reset_url}")
    
    # Send email
    subject = 'Password Reset Request'
    message = f'Click the following link to reset your password: {reset_url}'
    from_email = settings.DEFAULT_FROM_EMAIL
    
    try:
        logger.info(f"Attempting to send email from {from_email} to {email}")
        send_mail(subject, message, from_email, [email])
        logger.info("Email sent successfully")
    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}", exc_info=True)
        return Response({'error': 'Failed to send reset email'}, 
                       status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return Response({'message': 'If an account exists with this email, a password reset link has been sent.'}, 
                   status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password(request):
    uid = request.data.get('uid')
    token = request.data.get('token')
    new_password = request.data.get('password')
    
    logger.info(f"Password reset confirmation attempt - UID: {uid}, Token: {token}")
    
    try:
        uid = force_str(urlsafe_base64_decode(uid))
        user = User.objects.get(pk=uid)
        logger.info(f"User found for UID: {uid}")
    except (TypeError, ValueError, OverflowError, User.DoesNotExist) as e:
        logger.error(f"Invalid UID or user not found: {str(e)}", exc_info=True)
        return Response({'error': 'Invalid reset link'}, status=status.HTTP_400_BAD_REQUEST)
    
    if not default_token_generator.check_token(user, token):
        logger.error(f"Invalid token for user {user.email}")
        return Response({'error': 'Invalid reset link'}, status=status.HTTP_400_BAD_REQUEST)
    
    user.set_password(new_password)
    user.save()
    logger.info(f"Password successfully reset for user {user.email}")
    
    return Response({'message': 'Password has been reset successfully'}, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def delete_user(request):
    try:
        user = request.user
        
        # Delete Stripe customer and subscription if they exist
        try:
            from payment.models import StripeCustomer
            stripe_customer = StripeCustomer.objects.get(user=user)
            
            # Cancel any active subscriptions
            subscriptions = stripe.Subscription.list(
                customer=stripe_customer.customer_id,
                status='active'
            )
            for subscription in subscriptions.data:
                stripe.Subscription.delete(subscription.id)
            
            # Delete the Stripe customer
            stripe.Customer.delete(stripe_customer.customer_id)
            stripe_customer.delete()
        except StripeCustomer.DoesNotExist:
            pass  # No Stripe customer exists, which is fine
        
        # Delete the user
        user.delete()
        
        return Response({'message': 'User account deleted successfully'}, 
                       status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error deleting user: {str(e)}", exc_info=True)
        return Response({'error': 'Failed to delete user account'}, 
                       status=status.HTTP_500_INTERNAL_SERVER_ERROR)
