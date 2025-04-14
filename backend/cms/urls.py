from django.urls import path
from . import views

urlpatterns = [
    path('', views.cms_home, name='cms_home'),
    path('actions/', views.actions, name='actions'),
    path('import/', views.import_channel_videos, name='import_channel_videos'),
    path('import-playlist/', views.import_playlist_videos, name='import_playlist_videos'),
    path('bulk-import/', views.bulk_import_videos, name='bulk_import_videos'),
    path('review/', views.review_videos, name='review_videos'),
    path('update-statuses/', views.update_video_statuses, name='update_video_statuses'),
    path('videos/', views.list_all_videos, name='list_all_videos'),
    path('videos/<str:youtube_id>/', views.video_details, name='video_details'),
    path('videos/<str:youtube_id>/generate-snippets/', views.generate_snippets, name='generate_snippets'),
    path('videos/<str:youtube_id>/generate-translations/', views.generate_translations, name='generate_translations'),
    path('videos/<str:youtube_id>/publish/', views.publish_video, name='publish_video'),
    path('videos/<str:youtube_id>/reset-snippets/', views.reset_snippets, name='reset_snippets'),
    path('videos/<str:youtube_id>/export-snippets/', views.export_snippets_csv, name='export_snippets_csv'),
    path('mark-videos-without-arabic/', views.mark_videos_without_arabic_subtitles, name='mark_videos_without_arabic'),
    path('generate-snippets-all/', views.generate_snippets_for_all_shortlisted, name='generate_snippets_all'),
    path('generate-translations-all/', views.generate_translations_for_all_snippets, name='generate_translations_all'),
    path('bulk-check-subtitles/', views.bulk_check_subtitles, name='bulk_check_subtitles'),
    path('video/<str:youtube_id>/blacklist/', views.blacklist_video, name='blacklist_video'),
    path('set-frontend/', views.set_frontend, name='set_frontend'),
    path('update-priorities/', views.update_video_priorities, name='update_video_priorities'),
]
