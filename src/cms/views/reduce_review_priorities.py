
@staff_member_required
@require_http_methods(["POST"])
def reduce_review_priorities(request):
    """View to reduce priority for all videos on the current review page"""
    try:
        frontend = get_current_frontend(request)
        # Get the first 50 videos that need review, ordered by priority (descending) and youtube_id
        video_ids = Video.objects.filter(
            frontend=frontend,
            status=VideoStatus.NEEDS_REVIEW
        ).order_by('-priority', 'youtube_id')[:50].values_list('id', flat=True)
        
        # Update priorities for these specific videos
        Video.objects.filter(id__in=video_ids).update(priority=models.F('priority') - 1)
        messages.success(request, "Successfully reduced priority for all videos on the current page.")
        
    except Exception as e:
        messages.error(request, f"Error updating priorities: {str(e)}")
    
    return redirect('review_videos')
