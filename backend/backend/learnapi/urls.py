from django.contrib import admin
from django.urls import path, include
from .views import VideoListView, VideoSnippetsView, SnippetWordsView

urlpatterns = [
    path('videos/<str:language_code>/', VideoListView.as_view(), name='video-list'),
    path('videos/<str:youtube_id>/snippets/', VideoSnippetsView.as_view(), name='video-snippets'),
    path('videos/<str:youtube_id>/snippets/<int:snippet_index>/words/', SnippetWordsView.as_view(), name='snippet-words'),
]