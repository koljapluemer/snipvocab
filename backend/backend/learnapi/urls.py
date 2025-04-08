from django.contrib import admin
from django.urls import path, include
from .views import VideoListView

urlpatterns = [
    path('videos/<str:language_code>/', VideoListView.as_view(), name='video-list'),
]