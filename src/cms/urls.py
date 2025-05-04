from django.urls import path
from .views import (
    cms_home, actions, import_channel_videos, import_playlist_videos, bulk_import_videos,
    review_videos, update_video_statuses, list_all_videos, video_details, update_video_status,
    generate_snippets, generate_translations, publish_video, reset_snippets, export_snippets_csv,
    mark_videos_without_relevant_subtitles, generate_snippets_for_all_shortlisted,
    generate_translations_for_all_snippets, bulk_check_subtitles, blacklist_video, set_frontend,
    update_video_priorities, reduce_review_priorities, search_videos, enrich_video_metadata,
    publish_videos_with_many_snippets, user_statistics, manage_tags, remove_tag, add_tag,
    tag_autocomplete
)

app_name = 'cms'

urlpatterns = [
    path('', cms_home, name='cms_home'),
    path('actions/', actions, name='actions'),
    path('import/', import_channel_videos, name='import_channel_videos'),
    path('import-playlist/', import_playlist_videos, name='import_playlist_videos'),
    path('bulk-import/', bulk_import_videos, name='bulk_import_videos'),
    path('review/', review_videos, name='review_videos'),
    path('update-statuses/', update_video_statuses, name='update_video_statuses'),
    path('videos/', list_all_videos, name='list_all_videos'),
    path('videos/<str:youtube_id>/', video_details, name='video_details'),
    path('videos/<str:youtube_id>/update-status/', update_video_status, name='update_video_status'),
    path('videos/<str:youtube_id>/generate-snippets/', generate_snippets, name='generate_snippets'),
    path('videos/<str:youtube_id>/generate-translations/', generate_translations, name='generate_translations'),
    path('videos/<str:youtube_id>/publish/', publish_video, name='publish_video'),
    path('videos/<str:youtube_id>/reset-snippets/', reset_snippets, name='reset_snippets'),
    path('videos/<str:youtube_id>/export-snippets/', export_snippets_csv, name='export_snippets_csv'),
    path('mark-videos-without-arabic/', mark_videos_without_relevant_subtitles, name='mark_videos_without_arabic'),
    path('generate-snippets-all/', generate_snippets_for_all_shortlisted, name='generate_snippets_all'),
    path('generate-translations-all/', generate_translations_for_all_snippets, name='generate_translations_all'),
    path('bulk-check-subtitles/', bulk_check_subtitles, name='bulk_check_subtitles'),
    path('video/<str:youtube_id>/blacklist/', blacklist_video, name='blacklist_video'),
    path('set-frontend/', set_frontend, name='set_frontend'),
    path('update-priorities/', update_video_priorities, name='update_video_priorities'),
    path('reduce-review-priorities/', reduce_review_priorities, name='reduce_review_priorities'),
    path('search/', search_videos, name='search_videos'),
    path('enrich-metadata/', enrich_video_metadata, name='enrich_video_metadata'),
    path('publish-many-snippets/', publish_videos_with_many_snippets, name='publish_videos_with_many_snippets'),
    path('user-statistics/', user_statistics, name='user_statistics'),
    path('tags/', manage_tags, name='manage_tags'),
    path('tags/<int:tag_id>/', manage_tags, name='edit_tag'),
    path('videos/<str:youtube_id>/remove-tag/<int:tag_id>/', remove_tag, name='remove_tag'),
    path('videos/<str:youtube_id>/add-tag/', add_tag, name='add_tag'),
    path('tags/autocomplete/', tag_autocomplete, name='tag_autocomplete'),
]
