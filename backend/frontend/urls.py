from django.urls import path
from .views.videos.list import video_list
from .views.videos.detail import video_detail
from .views.snippets.detail import SnippetDetailView

urlpatterns = [
    path('videos/', video_list, name='video_list'),
    path('videos/<slug:youtube_id>/', video_detail, name='video_detail'),
    path('snippets/<int:pk>/practice/', SnippetDetailView.as_view(), name='snippet_practice'),
] 