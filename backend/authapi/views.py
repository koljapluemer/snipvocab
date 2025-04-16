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
from payment.models import Subscription
from django.contrib.auth import get_user_model

User = get_user_model()

# Create your views here.

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    form = CreateUserForm(request.data)
    if form.is_valid():
        user = form.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'message': 'User registered successfully',
            'user_id': user.id,
            'email': user.email,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)
    return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    # With JWT, we don't need to do anything on the server side
    # The client should simply discard the tokens
    return Response({'message': 'Logout successful'})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_info(request):
    subscription = None
    try:
        subscription = Subscription.objects.get(user=request.user)
    except Subscription.DoesNotExist:
        pass

    return Response({
        'email': request.user.email,
        'id': request.user.id,
        'subscription': {
            'status': subscription.status if subscription else None
        }
    })

@api_view(['POST'])
@permission_classes([AllowAny])
def request_password_reset(request):
    email = request.data.get('email')
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({'message': 'If an account exists with this email, a password reset link has been sent.'}, 
                       status=status.HTTP_200_OK)

    # Generate token and uid
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    
    # Create reset URL
    reset_url = f"{settings.FRONTEND_PASSWORD_RESET_URL}?uid={uid}&token={token}"
    
    # Send email
    subject = 'Password Reset Request'
    message = f'Click the following link to reset your password: {reset_url}'
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])
    
    return Response({'message': 'If an account exists with this email, a password reset link has been sent.'}, 
                   status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password(request):
    uid = request.data.get('uid')
    token = request.data.get('token')
    new_password = request.data.get('password')
    
    try:
        uid = force_str(urlsafe_base64_decode(uid))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return Response({'error': 'Invalid reset link'}, status=status.HTTP_400_BAD_REQUEST)
    
    if not default_token_generator.check_token(user, token):
        return Response({'error': 'Invalid reset link'}, status=status.HTTP_400_BAD_REQUEST)
    
    user.set_password(new_password)
    user.save()
    
    return Response({'message': 'Password has been reset successfully'}, status=status.HTTP_200_OK)
