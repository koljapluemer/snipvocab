from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_http_methods
from django.shortcuts import redirect
from django.contrib import messages

from shared.models import Video, VideoStatus

@staff_member_required
@require_http_methods(["POST"])
def reset_snippets(request, youtube_id):
    """View to reset snippets and translations for a video"""
    try:
        video = Video.objects.get(youtube_id=youtube_id)
        
        if video.status not in [VideoStatus.SNIPPETS_GENERATED, 
                              VideoStatus.SNIPPETS_AND_TRANSLATIONS_GENERATED, 
                              VideoStatus.LIVE]:
            messages.error(request, "Video must have snippets generated to reset them.")
            return redirect('video_details', youtube_id=youtube_id)
        
        # Delete snippets (this will cascade delete words and meanings)
        video.snippets.all().delete()
        
        # Reset status to shortlisted
        video.status = VideoStatus.SHORTLISTED
        video.save()
        
        messages.success(request, "Snippets and translations have been reset successfully.")
            
    except Video.DoesNotExist:
        messages.error(request, "Video not found.")
    except Exception as e:
        messages.error(request, f"Error resetting snippets: {str(e)}")
    
    return redirect('video_details', youtube_id=youtube_id)
