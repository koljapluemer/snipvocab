from django.contrib import admin
from django.urls import path, include

from learnapi.views.learning_events.learning_events import LearningEventsView
from learnapi.views.snippet_interaction.snippet_details import SnippetDetailsView
from learnapi.views.snippet_interaction.snippet_due_words import SnippetDueWordsView
from learnapi.views.snippet_interaction.snippet_all_words import SnippetAllWordsView
from learnapi.views.snippet_interaction.snippet_practice import SnippetPracticeView
from learnapi.views.utils.meanings import VideoListView
from learnapi.views.video_view.video_enriched_snippets import VideoEnrichedSnippetsView
from learnapi.views.video_view.video_snippets import VideoSnippetsView

urlpatterns = [
    path('videos/', VideoListView.as_view(), name='video-list'),
    path('videos/<str:youtube_id>/snippets/', VideoSnippetsView.as_view(), name='video-snippets'),
    path('videos/<str:youtube_id>/snippets/<int:index>/', SnippetDetailsView.as_view(), name='snippet-details'),
    path('videos/<str:youtube_id>/snippets/<int:index>/due-words/', SnippetDueWordsView.as_view(), name='snippet-due-words'),
    path('videos/<str:youtube_id>/snippets/<int:index>/all-words/', SnippetAllWordsView.as_view(), name='snippet-all-words'),
    path('videos/<str:youtube_id>/snippets/<int:index>/practice/', SnippetPracticeView.as_view(), name='snippet-practice'),
    path('videos/<str:youtube_id>/enriched-snippets/', VideoEnrichedSnippetsView.as_view(), name='video-enriched-snippets'),
    path('learning-events/', LearningEventsView.as_view(), name='learning-events'),
]