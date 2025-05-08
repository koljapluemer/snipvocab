from django.urls import path
from frontend.views.snippets.save_practiced_words import SavePracticedWordsView
from frontend.views.snippets.save_snippet_rating import SaveSnippetRatingView
from frontend.views.videos.list import video_list
from frontend.views.videos.detail import video_detail
from frontend.views.videos.share_view import video_share
from frontend.views.snippets.practice_and_watch import SnippetDetailView, SnippetWatchView
from frontend.views.snippets.redirect_to_next_snippet import redirect_to_next_snippet
from frontend.views.dashboard import dashboard
from frontend.views.onboarding import onboarding
from frontend.views.landing import landing

app_name = 'frontend'

urlpatterns = [
    path('', dashboard, name='dashboard'),
    path('landing/', landing, name='landing'),
    path('onboarding/', onboarding, name='onboarding'),
    path('videos/', video_list, name='video_list'),
    path('videos/<slug:youtube_id>/', video_detail, name='video_detail'),
    path('videos/<slug:youtube_id>/share/', video_share, name='video_share'),
    path('snippets/<int:pk>/practice/', SnippetDetailView.as_view(), name='snippet_practice'),
    path('snippets/<int:pk>/watch/', SnippetWatchView.as_view(), name='snippet_watch'),
    path('save_practiced_words/', SavePracticedWordsView.as_view(), name='save_practiced_words'),
    path('save_snippet_rating/', SaveSnippetRatingView.as_view(), name='save_snippet_rating'),
    path('redirect_to_next_snippet/<int:pk>/', redirect_to_next_snippet, name='redirect_to_next_snippet'),
] 