from django.shortcuts import render
from guest_user.decorators import allow_guest_user

@allow_guest_user
def landing(request):
    return render(request, 'frontend/landing/landing.html') 