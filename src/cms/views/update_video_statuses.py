from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_http_methods
from django.shortcuts import redirect
from django.contrib import messages
from django.http import JsonResponse

from shared.models import Video, VideoStatus

@staff_member_required
@require_http_methods(["POST"])
def update_video_statuses(request):
    """API endpoint to update multiple video statuses"""
    try:
        # Get all POST data
        post_data = request.POST
        
        # Check for bulk status update
        bulk_status = post_data.get('bulk_status')
        if bulk_status:
            # Get all videos in the current review queue
            videos = Video.objects.filter(status=VideoStatus.NEEDS_REVIEW).order_by('youtube_id')[:50]
            for video in videos:
                video.status = bulk_status
                video.save()
            messages.success(request, f"Successfully updated status for all videos to {bulk_status}.")
            return redirect('review_videos')
        
        # Process individual video statuses
        for key, value in post_data.items():
            if key.startswith('status_'):
                youtube_id = key.replace('status_', '')
                comment_key = f'comment_{youtube_id}'
                
                try:
                    video = Video.objects.get(youtube_id=youtube_id)
                    new_status = value
                    comment = post_data.get(comment_key, '')
                    
                    if new_status and new_status in [status[0] for status in VideoStatus.choices]:
                        video.status = new_status
                        video.comment = comment
                        video.save()
                except Video.DoesNotExist:
                    continue
        
        return redirect('review_videos')
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
