from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_http_methods
from shared.models import Video, VideoStatus

@staff_member_required
@require_http_methods(["POST"])
def blacklist_video(request, youtube_id):
    """View to blacklist a video"""
    try:
        video = Video.objects.get(youtube_id=youtube_id)
        video.status = VideoStatus.BLACKLISTED
        video.save()
        messages.success(request, "Video has been blacklisted successfully.")
    except Video.DoesNotExist:
        messages.error(request, "Video not found.")
    except Exception as e:
        messages.error(request, f"Error blacklisting video: {str(e)}")
    
    return redirect('cms:video_details', youtube_id=youtube_id)
