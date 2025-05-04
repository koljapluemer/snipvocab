from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_http_methods
from django.shortcuts import redirect
from django.contrib import messages

from shared.models import Video, Frontend, VideoStatus
from .get_current_frontend import get_current_frontend

@staff_member_required
@require_http_methods(["POST"])
def mark_videos_without_relevant_subtitles(request):
    """View to mark videos without target language subtitles as not relevant"""
    try:
        frontend = get_current_frontend(request)
        
        # Get videos for the current frontend that haven't been checked yet
        videos = Video.objects.filter(
            frontend=frontend,
            checked_for_relevant_subtitles=False
        ).exclude(
            status=VideoStatus.NOT_RELEVANT
        )
        
        marked_count = 0
        
        for video in videos:
            # Check if video has target language subtitles
            has_target_language = False
            if frontend == Frontend.ARABIC:
                has_target_language = any(lang.startswith('ar') for lang in video.available_subtitle_languages)
            else:  # German
                has_target_language = any(lang.startswith('de') for lang in video.available_subtitle_languages)
            
            if not has_target_language:
                video.status = VideoStatus.NOT_RELEVANT
                video.checked_for_relevant_subtitles = True
                video.save()
                marked_count += 1
        
        messages.success(request, f"Successfully marked {marked_count} videos without {frontend} subtitles as not relevant.")
    except Exception as e:
        messages.error(request, f"Error marking videos: {str(e)}")
    
    return redirect('cms:list_all_videos')
