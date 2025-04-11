from django.contrib import admin
from django.urls import path, include
from .views import VideoListView, VideoSnippetsView, SnippetDetailsView, SnippetDueWordsView, LearningEventsView, SnippetPracticeView, VideoEnrichedSnippetsView

urlpatterns = [
    path('videos/', VideoListView.as_view(), name='video-list'),
    path('videos/<str:youtube_id>/snippets/', VideoSnippetsView.as_view(), name='video-snippets'),
    path('videos/<str:youtube_id>/snippets/<int:index>/', SnippetDetailsView.as_view(), name='snippet-details'),
    path('videos/<str:youtube_id>/snippets/<int:index>/due-words/', SnippetDueWordsView.as_view(), name='snippet-due-words'),
    path('videos/<str:youtube_id>/snippets/<int:index>/practice/', SnippetPracticeView.as_view(), name='snippet-practice'),
    path('videos/<str:youtube_id>/enriched-snippets/', VideoEnrichedSnippetsView.as_view(), name='video-enriched-snippets'),
    path('learning-events/', LearningEventsView.as_view(), name='learning-events'),
    # admin
    path('admin/', admin.site.urls),
]