from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import login, logout, authenticate
from .forms import CreateUserForm

# Create your views here.

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    form = CreateUserForm(request.data)
    if form.is_valid():
        user = form.save()
        login(request, user)
        return Response({
            'message': 'User registered successfully',
            'user_id': user.id,
            'email': user.email
        }, status=status.HTTP_201_CREATED)
    return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    email = request.data.get('email')
    password = request.data.get('password')
    
    if not email or not password:
        return Response(
            {'error': 'Please provide both email and password'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user = authenticate(username=email, password=password)
    if user is not None:
        login(request, user)
        return Response({
            'message': 'Login successful',
            'user_id': user.id,
            'email': user.email
        })
    return Response(
        {'error': 'Invalid credentials'},
        status=status.HTTP_401_UNAUTHORIZED
    )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    logout(request)
    return Response({'message': 'Logout successful'})
