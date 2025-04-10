from django.urls import path
from . import views

urlpatterns = [
    path('', views.cms_home, name='cms_home'),
    path('import/', views.import_channel_videos, name='import_channel_videos'),
    path('review/', views.review_videos, name='review_videos'),
    path('update-statuses/', views.update_video_statuses, name='update_video_statuses'),
    path('videos/', views.list_all_videos, name='list_all_videos'),
    path('videos/<str:youtube_id>/', views.video_details, name='video_details'),
    path('videos/<str:youtube_id>/generate-snippets/', views.generate_snippets, name='generate_snippets'),
    path('videos/<str:youtube_id>/generate-translations/', views.generate_translations, name='generate_translations'),
]
