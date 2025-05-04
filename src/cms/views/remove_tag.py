@staff_member_required
@require_http_methods(["POST"])
def remove_tag(request, youtube_id, tag_id):
    """View to remove a tag from a video"""
    try:
        video = Video.objects.get(youtube_id=youtube_id)
        tag = Tag.objects.get(id=tag_id)
        video.tags.remove(tag)
        messages.success(request, f"Successfully removed tag '{tag.name}' from video.")
    except Video.DoesNotExist:
        messages.error(request, "Video not found.")
    except Tag.DoesNotExist:
        messages.error(request, "Tag not found.")
    except Exception as e:
        messages.error(request, f"Error removing tag: {str(e)}")
    
    return redirect('video_details', youtube_id=youtube_id)
