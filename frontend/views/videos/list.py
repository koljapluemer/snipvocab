from django.core.paginator import Paginator
from django.shortcuts import render
from django.conf import settings
from shared.models import Video, Frontend, VideoStatus
from guest_user.decorators import allow_guest_user
from frontend.models import VideoProgress
from frontend.interactors.get_videos_for_search import get_videos_for_search

@allow_guest_user
def video_list(request):
    # Get page number and search query from request
    page_number = request.GET.get('page', 1)
    search_term = request.GET.get('q', '').strip()
    
    # Use the feature flag to select the frontend language
    language_code = getattr(settings, 'LANGUAGE_TO_LEARN', 'de')
    frontend_value = language_code  # 'de' or 'ar'

    # Get videos using the search interactor (returns full queryset)
    videos_queryset, total_count = get_videos_for_search(
        search_term=search_term
    )

    # Ensure we're only showing videos for the current frontend
    videos_queryset = videos_queryset.filter(frontend=frontend_value)

    # Paginate the results
    paginator = Paginator(videos_queryset, 20)
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
        'search_term': search_term,
        'total_count': total_count,
    }
    
    return render(request, 'frontend/videos/list.html', context)
