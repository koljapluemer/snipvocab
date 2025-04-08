from django.contrib import admin
from django.urls import path, include
from .views import VideoListView, VideoSnippetsView

urlpatterns = [
    path('videos/<str:language_code>/', VideoListView.as_view(), name='video-list'),
    path('videos/<str:youtube_id>/snippets/', VideoSnippetsView.as_view(), name='video-snippets'),
]