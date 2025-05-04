from django.core.paginator import Paginator
from django.shortcuts import render
from django.conf import settings
from shared.models import Video, Frontend, VideoStatus
from guest_user.decorators import allow_guest_user
from frontend.models import VideoProgress

@allow_guest_user
def video_list(request):
    # Get page number from request, default to 1
    page_number = request.GET.get('page', 1)
    
    # Use the feature flag to select the frontend language
    language_code = getattr(settings, 'LANGUAGE_TO_LEARN', 'de')
    frontend_value = language_code  # 'de' or 'ar'

    # Get all live videos for the selected frontend
    videos = Video.objects.filter(
        status=VideoStatus.LIVE,
        frontend=frontend_value
    ).order_by('-added_at')
    
    # Paginate with 20 items per page
    paginator = Paginator(videos, 20)
    page_obj = paginator.get_page(page_number)

    # Attach last_practiced directly to each video object
    if request.user.is_authenticated:
        progresses = VideoProgress.objects.filter(user=request.user, video__in=page_obj.object_list)
        progress_map = {vp.video_id: vp.last_practiced for vp in progresses}
        for video in page_obj.object_list:
            video.last_practiced = progress_map.get(video.id)
    else:
        for video in page_obj.object_list:
            video.last_practiced = None
    
    context = {
        'videos': page_obj,
        'page_obj': page_obj,
    }
    
    return render(request, 'frontend/videos/list.html', context)
