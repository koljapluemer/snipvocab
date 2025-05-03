from django.core.paginator import Paginator
from django.shortcuts import render
from shared.models import Video, Frontend, VideoStatus

def video_list(request):
    # Get page number from request, default to 1
    page_number = request.GET.get('page', 1)
    
    # Get all live German videos
    videos = Video.objects.filter(
        status=VideoStatus.LIVE,
        frontend=Frontend.GERMAN
    ).order_by('-added_at')
    
    # Paginate with 20 items per page
    paginator = Paginator(videos, 20)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'videos': page_obj,
        'page_obj': page_obj,
    }
    
    return render(request, 'frontend/videos/list.html', context)
