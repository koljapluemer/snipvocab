from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.views.decorators.cache import never_cache
from youtube_transcript_api import YouTubeTranscriptApi

from shared.models import Video, Frontend, VideoStatus
from .get_current_frontend import get_current_frontend

@staff_member_required
@never_cache
def review_videos(request):
    """View to review videos that need review"""
    frontend = get_current_frontend(request)
    # Get first 50 videos that need review, ordered by priority (descending) and youtube_id
    videos = Video.objects.filter(frontend=frontend, status=VideoStatus.NEEDS_REVIEW).order_by('-priority', 'youtube_id')[:50]
    
    # Process each video to get available languages
    for video in videos:
        # Skip if already checked
        if video.checked_for_relevant_subtitles:
            continue
            
        try:
            # Get available languages using youtube_transcript_api
            available_languages = YouTubeTranscriptApi.list_transcripts(video.youtube_id)
            video.available_subtitle_languages = [lang.language_code for lang in available_languages]
            video.checked_for_relevant_subtitles = True
            video.save()
        except Exception as e:
            # If no transcripts available, set empty list
            video.available_subtitle_languages = []
            video.checked_for_relevant_subtitles = True  # Mark as checked even if there was an error
            video.save()
    
    context = {
        'videos': videos,
        'frontend': frontend
    }
    
    return render(request, 'review_videos.html', context)
