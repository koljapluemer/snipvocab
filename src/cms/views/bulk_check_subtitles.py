from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_http_methods
from shared.models import Video, VideoStatus
from youtube_transcript_api import YouTubeTranscriptApi
from .get_current_frontend import get_current_frontend

@staff_member_required
@require_http_methods(["POST"])
def bulk_check_subtitles(request):
    """View to check subtitles for all videos that haven't been checked yet"""
    try:
        frontend = get_current_frontend(request)
        
        # Get all videos that haven't been checked for Arabic subtitles and aren't marked as not relevant
        videos = Video.objects.filter(
            frontend=frontend,
            checked_for_relevant_subtitles=False
        ).exclude(
            status=VideoStatus.NOT_RELEVANT
        )
        
        processed_count = 0
        error_count = 0
        error_videos = []
        
        for video in videos:
            try:
                # Get available languages
                available_languages = YouTubeTranscriptApi.list_transcripts(video.youtube_id)
                video.available_subtitle_languages = [lang.language_code for lang in available_languages]
                video.checked_for_relevant_subtitles = True
                video.save()
                processed_count += 1
            except Exception as e:
                error_count += 1
                error_videos.append(f"{video.youtube_id} (Error: {str(e)})")
                # Mark as checked even if there was an error to avoid retrying
                video.checked_for_relevant_subtitles = True
                video.save()
        
        if processed_count > 0:
            messages.success(request, f"Successfully checked subtitles for {processed_count} videos.")
        if error_count > 0:
            messages.error(request, f"Failed to check subtitles for {error_count} videos: {', '.join(error_videos)}")
            
    except Exception as e:
        messages.error(request, f"Error checking subtitles: {str(e)}")
    
    return redirect('cms:actions')
