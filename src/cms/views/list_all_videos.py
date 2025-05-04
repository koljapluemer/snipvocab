
@staff_member_required
@never_cache
def list_all_videos(request):
    """View to list all videos with their status"""
    frontend = get_current_frontend(request)
    # Get page number and status filter from request
    page_number = request.GET.get('page', 1)
    status_filter = request.GET.get('status', '')
    comment_filter = request.GET.get('comment', '')
    
    # Get all videos ordered by status and youtube_id
    videos = Video.objects.filter(frontend=frontend)
    
    # Apply status filter if provided
    if status_filter:
        videos = videos.filter(status=status_filter)
    
    # Apply comment filter if provided
    if comment_filter:
        videos = videos.filter(comment__icontains=comment_filter)
    
    videos = videos.order_by('status', 'youtube_id')
    
    # Paginate the videos
    paginator = Paginator(videos, 20)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'videos': page_obj,
        'page_obj': page_obj,
        'status_filter': status_filter,
        'comment_filter': comment_filter,
        'status_choices': VideoStatus.choices,
        'frontend': frontend
    }
    
    return render(request, 'list_all_videos.html', context)
