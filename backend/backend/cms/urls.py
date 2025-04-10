from django.urls import path
from . import views

urlpatterns = [
    path('channel-videos/', views.list_channel_videos, name='list_channel_videos'),
    path('videos/<str:youtube_id>/status/', views.update_video_status, name='update_video_status'),
]
