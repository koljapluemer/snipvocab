
@staff_member_required
@require_http_methods(["POST"])
def publish_video(request, youtube_id):
    """View to publish a video"""
    try:
        video = Video.objects.get(youtube_id=youtube_id)
        
        if video.status != VideoStatus.SNIPPETS_AND_TRANSLATIONS_GENERATED:
            messages.error(request, "Video must have snippets and translations generated before publishing.")
            return redirect('video_details', youtube_id=youtube_id)
        
        video.status = VideoStatus.LIVE
        video.save()
        
        messages.success(request, "Video has been published successfully.")
            
    except Video.DoesNotExist:
        messages.error(request, "Video not found.")
    except Exception as e:
        messages.error(request, f"Error publishing video: {str(e)}")
    
    return redirect('video_details', youtube_id=youtube_id)
