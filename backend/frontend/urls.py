from django.urls import path
from .views.videos.list import video_list
from .views.videos.detail import video_detail

urlpatterns = [
    path('videos/', video_list, name='video_list'),
    path('videos/<slug:youtube_id>/', video_detail, name='video_detail'),
] 