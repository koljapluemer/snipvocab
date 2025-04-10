from django.contrib import admin
from django.urls import path, include
from .views import VideoListView, VideoSnippetsView, SnippetDetailsView

urlpatterns = [
    path('videos/', VideoListView.as_view(), name='video-list'),
    path('videos/<str:youtube_id>/snippets/', VideoSnippetsView.as_view(), name='video-snippets'),
    path('videos/<str:youtube_id>/snippets/<int:index>/', SnippetDetailsView.as_view(), name='snippet-details'),
]