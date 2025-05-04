@staff_member_required
@require_http_methods(["POST"])
def update_video_status(request, youtube_id):
    """View to update a single video's status"""
    try:
        video = Video.objects.get(youtube_id=youtube_id)
        new_status = request.POST.get('status')
        
        if new_status and new_status in [status[0] for status in VideoStatus.choices]:
            video.status = new_status
            video.save()
            messages.success(request, f"Successfully updated video status to {new_status}.")
        else:
            messages.error(request, "Invalid status provided.")
            
    except Video.DoesNotExist:
        messages.error(request, "Video not found.")
    except Exception as e:
        messages.error(request, f"Error updating video status: {str(e)}")
    
    return redirect('video_details', youtube_id=youtube_id)
