from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_http_methods
from django.shortcuts import redirect
from django.contrib import messages
from django.db import models
from django.urls import reverse

from shared.models import Video, Frontend, VideoStatus
from .get_current_frontend import get_current_frontend

@staff_member_required
@require_http_methods(["POST"])
def update_video_priorities(request):
    """View to update priorities for all videos in the current filter"""
    try:
        # Get the current filter parameters
        status_filter = request.POST.get('status_filter', '')
        comment_filter = request.POST.get('comment_filter', '')
        frontend = get_current_frontend(request)
        
        # Get all videos matching the current filter
        videos = Video.objects.filter(frontend=frontend)
        
        if status_filter:
            videos = videos.filter(status=status_filter)
        if comment_filter:
            videos = videos.filter(comment__icontains=comment_filter)
        
        # Get the action (increase or decrease)
        action = request.POST.get('action')
        
        # Update priorities
        if action == 'increase':
            videos.update(priority=models.F('priority') + 1)
            messages.success(request, "Successfully increased priority for all videos in the current filter.")
        elif action == 'decrease':
            videos.update(priority=models.F('priority') - 1)
            messages.success(request, "Successfully decreased priority for all videos in the current filter.")
        
    except Exception as e:
        messages.error(request, f"Error updating priorities: {str(e)}")
    
    # Redirect back to the list view with the same filters
    redirect_url = reverse('cms:list_all_videos')
    if status_filter:
        redirect_url += f"?status={status_filter}"
    if comment_filter:
        redirect_url += f"{'&' if status_filter else '?'}comment={comment_filter}"
    
    return redirect(redirect_url)
