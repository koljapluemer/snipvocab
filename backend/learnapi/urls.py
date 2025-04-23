from django.contrib import admin
from django.urls import path, include

from learnapi.views.video_list.video_list import VideoListView
from learnapi.views.video_list.video_list_for_tag import VideoListForTagView
from learnapi.views.video_list.video_list_newly_added import VideoListNewlyAddedView
from learnapi.views.video_list.video_list_by_view import VideoListByViewView
from learnapi.views.tags.common_tags import RandomCommonTagView
from learnapi.views.learning_events.learning_events import LearningEventsView
from learnapi.views.snippet_interaction.snippet_details import SnippetDetailsView
from learnapi.views.snippet_interaction.snippet_due_words import SnippetDueWordsView
from learnapi.views.snippet_interaction.snippet_all_words import SnippetAllWordsView
from learnapi.views.snippet_interaction.snippet_practice import SnippetPracticeView
from learnapi.views.video_view.video_enriched_snippets import VideoEnrichedSnippetsView
from learnapi.views.video_view.video_snippets import VideoSnippetsView
from learnapi.views.video_view.video_progress import VideoProgressView
from learnapi.views.video_list.videos_for_onboarding import VideosForOnboardingView

urlpatterns = [
    path('videos/', VideoListView.as_view(), name='video-list'),
    path('videos/new/', VideoListNewlyAddedView.as_view(), name='video-list-new'),
    path('videos/popular/', VideoListByViewView.as_view(), name='video-list-popular'),
    path('videos/tag/<str:tag_name>/', VideoListForTagView.as_view(), name='video-list-for-tag'),
    path('tags/random/', RandomCommonTagView.as_view(), name='random-common-tag'),
    path('videos/<str:youtube_id>/snippets/', VideoSnippetsView.as_view(), name='video-snippets'),
    path('videos/<str:youtube_id>/snippets/<int:index>/', SnippetDetailsView.as_view(), name='snippet-details'),
    path('videos/<str:youtube_id>/snippets/<int:index>/due-words/', SnippetDueWordsView.as_view(), name='snippet-due-words'),
    path('videos/<str:youtube_id>/snippets/<int:index>/all-words/', SnippetAllWordsView.as_view(), name='snippet-all-words'),
    path('videos/<str:youtube_id>/snippets/<int:index>/practice/', SnippetPracticeView.as_view(), name='snippet-practice'),
    path('videos/<str:youtube_id>/enriched-snippets/', VideoEnrichedSnippetsView.as_view(), name='video-enriched-snippets'),
    path('videos/<str:youtube_id>/progress/', VideoProgressView.as_view(), name='video-progress'),
    path('learning-events/', LearningEventsView.as_view(), name='learning-events'),
    path('videos/onboarding/', VideosForOnboardingView.as_view(), name='get-onboarding-videos'),
]