from django.urls import path
from . import views

urlpatterns = [
    path('create-checkout-session/', views.create_checkout_session, name='create-checkout-session'),
    path('create-portal-session/', views.create_customer_portal_session, name='create-portal-session'),
    path('subscription-info/', views.get_subscription_info, name='subscription-info'),
    path('webhook/', views.stripe_webhook, name='stripe-webhook'),
]
